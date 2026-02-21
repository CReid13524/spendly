import enum
from http import HTTPStatus

from flask import request, g
from flask_restx import Resource, Namespace, fields
from iso4217 import Currency
from werkzeug.datastructures import FileStorage

from FlaskApp.domainmodel.upload import SupportedBank
from FlaskApp.infra.db import SessionLocal
from FlaskApp.infra.exceptions import ValidationError
from FlaskApp.infra.models import NullableString
from FlaskApp.domainmodel.account import AccountType, AccountAttribute
from FlaskApp.infra.services import CREATED_RESPONSE, OK_RESPONSE, make_ok_response, require_auth, models, validate_uuid
from FlaskApp.infra.unit_of_work import SqlAlchemyUnitOfWork
from FlaskApp.routes.accounts.services import create_account, delete_upload, get_accounts, get_uploads, update_account, delete_account, upload_csv
from FlaskApp.routes.accounts.presentation import account_domain_to_json, upload_domain_to_json

ns = Namespace('accounts', description='Operations related to accounts')


# region Account Models
account_item_model = ns.model('Account', {
    'id': fields.String(required=True, description='The account unique identifier', example='a1b2c3d4-e5f6-a1b2-c3d4-e5f6a1b2c3d4'),
    'name': fields.String(required=True, description='The name of the account', example='Everyday Checking'),
    'type': fields.String(required=True, description='The type of the account', example='checking', enum=[e.value for e in AccountType]),
    'formatted_account': fields.String(required=True, description='The formatted account number', example='12-3456-7890123-00'),
    'attributes': fields.List(fields.String, required=True, description='List of account attributes', example=[e.value for e in AccountAttribute], enum=[e.value for e in AccountAttribute]),
    'currency': fields.String(required=True, description='The currency of the account', example='NZD'),
    'current_balance': NullableString(required=True, description='The current balance of the account', example='1000.00'),
    'available_balance': NullableString(required=True, description='The available balance of the account', example='800.00'),
    'status': fields.String(required=True, description='The status of the account', example='active'),
    'created': fields.DateTime(required=True, description='The date and time when the account was created', example='2024-01-01T12:00:00Z'),
    'credit_limit': NullableString(description='The credit limit of the account (if applicable)', example='5000.00'),
    'overdrawn': fields.Boolean(required=True, description='Whether the account is overdrawn or not', example=False),
    'provider_name': fields.String(required=True, description='The name of the account provider', example='Bank of Example'),
    'provider_logo': fields.String(required=True, description='The logo of the account provider', example='https://example.com/logo.png'),
})

accounts_model = ns.model('AccountListResponse', {
    'success': fields.Boolean(required=True, description='Indicates if the request was successful'),
    'accounts': fields.List(fields.Nested(account_item_model), description='List of accounts')
})


editable_account_model = ns.model('AccountUpdate', {
    'name': fields.String(required=True, description='The name of the account', example='Everyday Checking'),
    'type': fields.String(required=True, description='The type of the account', example='checking', enum=[e.value for e in AccountType]),
    'formatted_account': fields.String(required=True, description='The formatted account number', example='12-3456-7890123-00'),
    'attributes': fields.List(fields.String, required=True, description='List of account attributes', example=[e.value for e in AccountAttribute], enum=[e.value for e in AccountAttribute]),
    'currency': fields.String(required=True, description='The currency of the account. ISO 4217 currency code', example='NZD'), # Iso 4217 currency code
    'credit_limit': NullableString(required=True, description='The credit limit of the account (if applicable)', example="5000.00"),
})

# endregion

# region Upload Models and Parsers

upload_transaction_model = ns.model('UploadTransactionResponse', {
    "success": fields.Boolean(description='Indicates if the request was successful', example=True),
    "uploads": fields.List(fields.Nested(ns.model('UploadItem', {
        'id': fields.String(readOnly=True, description='The unique identifier of an upload',
                            example="a1b2c3d4-e5f6-a1b2-c3d4-e5f6a1b2c3d4"),
        'filename': fields.String(description='Original filename of the uploaded CSV file', example="transactions.csv"),
        'bank': fields.String(description='Bank associated with the uploaded transactions', example="ANZ"),
        'created': fields.DateTime(description='Timestamp when the file was uploaded', example="2024-01-01T12:00:00Z"),
        'transaction_count': fields.Integer(description='Number of transactions associated with the upload',
                                            example=100),
    })))
})

# Parser
upload_csv_parser = ns.parser()
upload_csv_parser.add_argument('file', location='files', type=FileStorage, required=True)
upload_csv_parser.add_argument('bank', location='form', type=str, choices=[bank.value for bank in SupportedBank],
                               help=f'Bank associated with the uploaded transactions.', required=True)

# endregion


@ns.route('')
class Account(Resource):
    @ns.response(HTTPStatus.OK, 'Success', accounts_model)
    @require_auth(ns=ns)
    def get(self):
        """Get all accounts for the authenticated user"""
        uow = SqlAlchemyUnitOfWork(SessionLocal)
        accounts = get_accounts(uow=uow, user=g.current_user)
        accounts_json = [account_domain_to_json(a) for a in accounts]
        return make_ok_response(accounts=accounts_json)

    @ns.expect(editable_account_model, validate=True)
    @ns.response(HTTPStatus.CREATED, 'Success', models['OK'])
    @ns.response(HTTPStatus.BAD_REQUEST, 'Validation Error', models['BadRequest'])
    @require_auth(ns=ns)
    def post(self):
        """Create a new account for the authenticated user"""
        data = request.get_json()

        # Validation
        if data['currency'] not in Currency:
            raise ValidationError(f"Invalid currency code: {data['currency']}. Must be a valid ISO 4217 currency code.")
        if data['attributes']:
            for attr in data['attributes']:
                if attr not in AccountAttribute._value2member_map_:
                    raise ValidationError(f"Invalid account attribute: {attr}. Must be one of {[e.value for e in AccountAttribute]}")
        if data['type'] not in AccountType._value2member_map_:
            raise ValidationError(f"Invalid account type: {data['type']}. Must be one of {[e.value for e in AccountType]}")

        uow = SqlAlchemyUnitOfWork(SessionLocal)
        create_account(uow, user=g.current_user, **data)
        return CREATED_RESPONSE



@ns.route('/<string:account_id>')
class AccountById(Resource):
    @ns.expect(editable_account_model, validate=True)
    @ns.response(HTTPStatus.OK, 'Success', models['OK'])
    @ns.response(HTTPStatus.BAD_REQUEST, 'Validation Error', models['BadRequest'])
    @require_auth(ns=ns)
    def put(self, account_id):
        """Update an existing account for the authenticated user"""
        data = request.get_json()

        # Validation
        validate_uuid(account_id, field_name='id')
        if data['currency'] not in Currency:
            raise ValidationError(f"Invalid currency code: {data['currency']}. Must be a valid ISO 4217 currency code.")
        if data['attributes']:
            for attr in data['attributes']:
                if attr not in AccountAttribute._value2member_map_:
                    raise ValidationError(f"Invalid account attribute: {attr}. Must be one of {[e.value for e in AccountAttribute]}")
        if data['type'] not in AccountType._value2member_map_:
            raise ValidationError(f"Invalid account type: {data['type']}. Must be one of {[e.value for e in AccountType]}")

        uow = SqlAlchemyUnitOfWork(SessionLocal)
        update_account(uow, user=g.current_user, account_id=account_id, **data)
        return OK_RESPONSE

    @ns.expect(editable_account_model, validate=True)
    @ns.response(HTTPStatus.OK, 'Success', models['OK'])
    @ns.response(HTTPStatus.BAD_REQUEST, 'Validation Error', models['BadRequest'])
    @require_auth(ns=ns)
    def delete(self, account_id):
        """Delete an existing account"""
        validate_uuid(account_id, field_name='id')
        uow = SqlAlchemyUnitOfWork(SessionLocal)
        delete_account(uow, user=g.current_user, account_id=account_id)
        return OK_RESPONSE

@ns.route('/<string:account_id>/upload')
class CSVUpload(Resource):

    @ns.response(HTTPStatus.OK, 'OK', upload_transaction_model)
    @ns.response(HTTPStatus.BAD_REQUEST, 'Validation Error', models['BadRequest'])
    @ns.param('account_id', description='The unique identifier of the account', example="a1b2c3d4-e5f6-a1b2-c3d4-e5f6a1b2c3d4")
    @ns.doc(
        description="Get a list of uploaded CSV files. This will include metadata about the upload but not the transactions themselves.")
    @require_auth(ns=ns)
    def get(self, account_id):
        """Get a list of uploaded CSV files."""
        uow = SqlAlchemyUnitOfWork(SessionLocal)
        uploads = get_uploads(uow=uow, user=g.current_user)
        uploads_json = [upload_domain_to_json(upload) for upload in uploads]
        return {"success": True, "uploads": uploads_json}, HTTPStatus.OK

    @ns.response(HTTPStatus.CREATED, 'OK', models['OK'])
    @ns.response(HTTPStatus.BAD_REQUEST, 'Validation Error', models['BadRequest'])
    @ns.expect(upload_csv_parser, validate=True)
    @ns.param('account_id', description='The unique identifier of the account', example="a1b2c3d4-e5f6-a1b2-c3d4-e5f6a1b2c3d4")
    @ns.doc(
        description="Upload a CSV file of transactions. Supported banks: ANZ, Kiwibank. CSV format must match the format provided by the bank's online transaction export.")
    @require_auth(ns=ns)
    def post(self, account_id):
        """Upload a CSV file of transactions."""

        # Validation
        args = upload_csv_parser.parse_args()
        file = args.get('file')
        bank = args.get('bank')
        validate_uuid(account_id, "account_id")
        if not file:
            raise ValidationError("No file provided")
        filename = file.filename.lower()
        if not (filename.endswith('.csv')):
            raise ValidationError("Unsupported file format. Only CSV files are supported.")
        if not bank.lower() in [bank.value for bank in SupportedBank]:
            raise ValidationError(f"Unsupported bank. Supported banks: {[bank.value for bank in SupportedBank]}")

        uow = SqlAlchemyUnitOfWork(SessionLocal)
        upload_csv(uow=uow, file=file, user=g.current_user, bank=bank, account_id=account_id)
        return CREATED_RESPONSE


@ns.route('/<string:account_id>/upload/<string:upload_id>')
class UploadByID(Resource):

    @ns.response(HTTPStatus.OK, 'OK', models['OK'])
    @ns.response(HTTPStatus.BAD_REQUEST, 'Validation Error', models['BadRequest'])
    @ns.param('upload_id', description='The unique identifier of the upload', example="a1b2c3d4-e5f6-a1b2-c3d4-e5f6a1b2c3d4")
    @ns.param('account_id', description='The unique identifier of the account', example="a1b2c3d4-e5f6-a1b2-c3d4-e5f6a1b2c3d4")
    @ns.doc(
        description="Delete an uploaded CSV file of transactions. This will delete any transactions that were created from the upload.")
    @require_auth(ns=ns)
    def delete(self, _, upload_id):
        """Delete an uploaded CSV file of transactions."""

        # Validation
        validate_uuid(upload_id, "upload_id")

        uow = SqlAlchemyUnitOfWork(SessionLocal)
        delete_upload(uow=uow, user=g.current_user, upload_id=upload_id)
        return OK_RESPONSE