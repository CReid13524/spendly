import enum
from http import HTTPStatus

from flask import request, g
from flask_restx import Resource, Namespace, fields, reqparse
from werkzeug.datastructures import FileStorage

from FlaskApp.infra.db import SessionLocal
from FlaskApp.infra.exceptions import ValidationError
from FlaskApp.infra.models import NullableFloat, NullableString, parse_bool, parse_bool_or_other
from FlaskApp.infra.services import CREATED_RESPONSE, OK_RESPONSE, make_ok_response, require_auth, models
from FlaskApp.infra.unit_of_work import SqlAlchemyUnitOfWork
from FlaskApp.routes.transactions.presentation import transaction_domain_to_json, upload_domain_to_json
from FlaskApp.routes.transactions.services import create_transaction, delete_transaction, delete_upload, \
    get_transactions, get_uploads, update_transaction, patch_transaction, upload_csv, update_transaction_locations

ns = Namespace('transactions', description='Operations related to transactions')


# region Enums
class SupportedBank(fields.String, enum.Enum):
    ANZ = 'anz'
    KIWIBANK = 'kiwibank'


class SupportedSort(fields.String, enum.Enum):
    DATE = 'date'
    DATE_DESC = '-date'
    AMOUNT = 'amount'
    AMOUNT_DESC = '-amount'
    CREATED = 'created'
    CREATED_DESC = '-created'


# endregion

# region Transaction Models and Parsers
transaction_item_model = ns.model('TransactionItem', {
    'id': fields.String(readOnly=True, description='The unique identifier of a transaction',
                        example="a1b2c3d4-e5f6-a1b2-c3d4-e5f6a1b2c3d4"),
    'amount': fields.Float(required=True, description='Transaction amount', example=100.50),
    'date': fields.Date(required=True, description='Transaction date', example="2024-01-01"),
    'description': fields.String(required=True, description='Transaction description', example="Grocery shopping"),
    'balance': NullableFloat(required=True, description='Account balance after the transaction', example=1500.75),
    'pending': fields.Boolean(required=True, description='Indicates if the transaction is pending', example=False),
    'type': NullableString(required=True, description='Transaction type', example="VISA PURCHASE"),
    'status': fields.String(required=True, description='Transaction status', example="active"),
    'created': fields.DateTime(required=True, description='Timestamp when the transaction was created',
                               example="2024-01-01T12:00:00Z"),
    'latitude': NullableFloat(required=True, description='Latitude of the transaction location', example=-36.848378776),
    'longitude': NullableFloat(required=True, description='Longitude of the transaction location',
                               example=174.764381777),
    'category_id': NullableString(required=True, description='ID of the associated category',
                                  example="a1b2c3d4-e5f6-a1b2-c3d4-e5f6a1b2c3d4"),
    'account_id': fields.String(required=True, description='ID of the associated account',
                                example="a1b2c3d4-e5f6-a1b2-c3d4-e5f6a1b2c3d4"),
    'merchant_id': NullableString(required=True, description='ID of the associated merchant',
                                  example="a1b2c3d4-e5f6-a1b2-c3d4-e5f6a1b2c3d4"),
})

new_transaction_model = ns.model('NewTransaction', {
    'amount': fields.Float(required=True, description='Transaction amount', example=100.50),
    'date': fields.Date(required=True, description='Transaction date', example="2024-01-01"),
    'description': fields.String(required=True, description='Transaction description', example="Grocery shopping"),
    'balance': NullableFloat(required=True, description='Account balance after the transaction', example=6900.00),
    'pending': fields.Boolean(required=True, description='Indicates if the transaction is pending', example=False,
                              default=False),
    'type': NullableString(required=True, description='Transaction type', example="VISA PURCHASE"),
    'latitude': NullableFloat(required=True, description='Latitude of the transaction location', example=-36.848378776),
    'longitude': NullableFloat(required=True, description='Longitude of the transaction location',
                               example=174.764381777),
    'category_id': NullableString(required=True, description='ID of the associated category',
                                  example="a1b2c3d4-e5f6-a1b2-c3d4-e5f6a1b2c3d4"),
    'account_id': fields.String(required=True, description='ID of the associated account',
                                example="a1b2c3d4-e5f6-a1b2-c3d4-e5f6a1b2c3d4"),
    'merchant_id': NullableString(required=True, description='ID of the associated merchant',
                                  example="a1b2c3d4-e5f6-a1b2-c3d4-e5f6a1b2c3d4"),
})

transaction_patch_model = ns.model('PatchTransaction', {
    'id': fields.String(required=True, description='The unique identifier of a transaction',
                        example="a1b2c3d4-e5f6-a1b2-c3d4-e5f6a1b2c3d4"),
    'category_id': NullableString(required=False, description='ID of the associated category',
                                  example="a1b2c3d4-e5f6-a1b2-c3d4-e5f6a1b2c3d4"),
    'account_id': fields.String(required=False, description='ID of the associated account',
                                example="a1b2c3d4-e5f6-a1b2-c3d4-e5f6a1b2c3d4"),
    'merchant_id': NullableString(required=False, description='ID of the associated merchant',
                                  example="a1b2c3d4-e5f6-a1b2-c3d4-e5f6a1b2c3d4"),
})

transaction_model = ns.model('Transaction', {
    "success": fields.Boolean(description='Indicates if the request was successful', example=True),
    "transactions": fields.List(fields.Nested(transaction_item_model))
})

transaction_id_model = ns.model('transaction_id', {
    'id': fields.String(required=True, description='The unique identifier of a transaction',
                        example="a1b2c3d4-e5f6-a1b2-c3d4-e5f6a1b2c3d4")
})

# Parser for GET /transactions


get_transactions_parser = reqparse.RequestParser()
get_transactions_parser.add_argument('start_date', type=str, required=False,
                                     help='Start date for filtering transactions (ISO 8601 format)')
get_transactions_parser.add_argument('end_date', type=str, required=False,
                                     help='End date for filtering transactions (ISO 8601 format)')
get_transactions_parser.add_argument('search', type=str, required=False,
                                     help='Search term to filter transactions by description. Case-insensitive substring match.')
get_transactions_parser.add_argument('type', type=str, required=False,
                                     help='Filter transactions by type. Case-insensitive exact match.')
get_transactions_parser.add_argument('pending', type=parse_bool, required=False,
                                     help='Filter transactions by pending status. Boolean.')
get_transactions_parser.add_argument('status', type=str, required=False, default='active',
                                     choices=['active', 'deleted'], help="Filter transactions by status.")
get_transactions_parser.add_argument('category_id', type=lambda x: parse_bool_or_other(x, str), required=False,
                                     help='Category ID for filtering transactions. Boolean indicates existence filter.')
get_transactions_parser.add_argument('account_id', type=str, required=False,
                                     help='Account ID for filtering transactions.')
get_transactions_parser.add_argument('merchant_id', type=lambda x: parse_bool_or_other(x, str), required=False,
                                     help='Merchant ID for filtering transactions. Boolean indicates existence filter.')
get_transactions_parser.add_argument('start_amount', type=float, required=False,
                                     help='Minimum amount for filtering transactions.')
get_transactions_parser.add_argument('end_amount', type=float, required=False,
                                     help='Maximum amount for filtering transactions.')
get_transactions_parser.add_argument('start_lat', type=lambda x: parse_bool_or_other(x, float), required=False,
                                     help='Minimum latitude for filtering transactions. Boolean indicates existence filter. No end_lat provided means exact match.')
get_transactions_parser.add_argument('end_lat', type=float, required=False,
                                     help='Maximum latitude for filtering transactions.')
get_transactions_parser.add_argument('start_lng', type=lambda x: parse_bool_or_other(x, float), required=False,
                                     help='Minimum longitude for filtering transactions. Boolean indicates existence filter. No end_lng provided means exact match.')
get_transactions_parser.add_argument('end_lng', type=float, required=False,
                                     help='Maximum longitude for filtering transactions.')
get_transactions_parser.add_argument('page', type=int, required=False, default=1, help='Page number for pagination.')
get_transactions_parser.add_argument('per_page', type=int, required=False, default=20,
                                     help='Number of transactions per page for pagination.')
get_transactions_parser.add_argument('sort', type=str, required=False, default='-date',
                                     choices=[e.value for e in SupportedSort],
                                     help=f"Field to sort by. Prefix with '-' for descending order.")


# endregion

# region Upload Models and Parsers
upload_id_model = ns.model('upload_id', {
    'id': fields.String(required=True, description='The unique identifier of a upload',
                        example="a1b2c3d4-e5f6-a1b2-c3d4-e5f6a1b2c3d4")
})

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

# Parsers for POST /transactions/upload
upload_csv_parser = ns.parser()
upload_csv_parser.add_argument('file', location='files', type=FileStorage, required=True)
upload_csv_parser.add_argument('bank', location='form', type=str, choices=[bank.value for bank in SupportedBank],
                               help=f'Bank associated with the uploaded transactions.', required=True)
upload_csv_parser.add_argument('account_id', location='form', type=str,
                               help='ID of the account to associate the uploaded transactions with. Example: "a1b2c3d4-e5f6-a1b2-c3d4-e5f6a1b2c3d4"',
                               required=True)

# endregion

# region Mapping Models
transaction_map_model = ns.model('TransactionMap', {
    "id": fields.String(required=True, description='The unique identifier of a transaction',
                        example="a1b2c3d4-e5f6-a1b2-c3d4-e5f6a1b2c3d4"),
    "latitude": NullableFloat(required=True, description='Latitude of the transaction location', example=-36.848378776),
    "longitude": NullableFloat(required=True, description='Longitude of the transaction location',
                               example=174.764381777),
})


# endregion


@ns.route('')
class Transaction(Resource):

    @ns.response(HTTPStatus.OK, 'OK', transaction_model)
    @ns.expect(get_transactions_parser, validate=True)
    @ns.doc(
        description="Get a list of transactions with optional filters. By default, only active transactions are returned in date descending order. All filters are optional and can be combined. Pagination and sorting are supported.")
    @require_auth(ns=ns)
    def get(self):
        """Get transactions with optional filters."""
        uow = SqlAlchemyUnitOfWork(SessionLocal)
        args = get_transactions_parser.parse_args()
        filters = {k: v for k, v in args.items() if v is not None}
        transactions = get_transactions(uow=uow, user=g.current_user, **filters)
        transactions_json = [transaction_domain_to_json(transaction) for transaction in transactions]
        return make_ok_response(transactions=transactions_json)

    @ns.response(HTTPStatus.CREATED, 'OK', models['OK'])
    @ns.expect(new_transaction_model, validate=True)
    @ns.doc(
        description="Create a new transaction. All fields are required. If the transaction is not associated with a category or merchant, set category_id or merchant_id to null.")
    @require_auth(ns=ns)
    def post(self):
        """Create a new transaction."""
        uow = SqlAlchemyUnitOfWork(SessionLocal)
        data = request.get_json()
        create_transaction(uow=uow, user=g.current_user, **data)
        return CREATED_RESPONSE

    @ns.response(HTTPStatus.OK, 'OK', models['OK'])
    @ns.expect(transaction_item_model, validate=True)
    @ns.doc(
        description="Update an existing transaction. All fields are required, even if not being updated. Use the PATCH endpoint to update only category, merchant, or account relationships.")
    @require_auth(ns=ns)
    def put(self):
        # TODO: Currently akahu transactions do not persist updates between syncs
        """Update an existing transaction."""
        uow = SqlAlchemyUnitOfWork(SessionLocal)
        data = request.get_json()
        update_transaction(uow=uow, user=g.current_user, **data)
        return OK_RESPONSE

    @ns.response(HTTPStatus.OK, 'OK', models['OK'])
    @ns.expect(transaction_id_model, validate=True)
    @require_auth(ns=ns)
    def delete(self):
        # TODO: Currently akahu transactions do not persist deletions between syncs
        """Delete an existing transaction."""
        uow = SqlAlchemyUnitOfWork(SessionLocal)
        data = request.get_json()
        delete_transaction(uow=uow, user=g.current_user, transaction_id=data['id'])
        return OK_RESPONSE

    @ns.response(HTTPStatus.OK, 'OK', models['OK'])
    @ns.expect(transaction_patch_model, validate=True)
    @ns.doc(
        description="Update the category, merchant, or account of an existing transaction. This is intended for updating relationships only, use the PUT endpoint to update other transaction fields.")
    @require_auth(ns=ns)
    def patch(self):
        """Update category, merchant, or account of an existing transaction."""
        uow = SqlAlchemyUnitOfWork(SessionLocal)
        data = request.get_json()
        patch_transaction(uow=uow, user=g.current_user, **data)
        return OK_RESPONSE


@ns.route('/upload')
class CSVUpload(Resource):

    @ns.response(HTTPStatus.OK, 'OK', upload_transaction_model)
    @ns.doc(
        description="Get a list of uploaded CSV files. This will include metadata about the upload but not the transactions themselves.")
    @require_auth(ns=ns)
    def get(self):
        """Get a list of uploaded CSV files."""
        uow = SqlAlchemyUnitOfWork(SessionLocal)
        uploads = get_uploads(uow=uow, user=g.current_user)
        uploads_json = [upload_domain_to_json(upload) for upload in uploads]
        return {"success": True, "uploads": uploads_json}, HTTPStatus.OK

    @ns.response(HTTPStatus.CREATED, 'OK', models['OK'])
    @ns.response(HTTPStatus.BAD_REQUEST, 'Bad Request', models['BadRequest'])
    @ns.expect(upload_csv_parser, validate=True)
    @ns.doc(
        description="Upload a CSV file of transactions. Supported banks: ANZ, Kiwibank. CSV format must match the format provided by the bank's online transaction export.")
    @require_auth(ns=ns)
    def post(self):
        """Upload a CSV file of transactions."""
        args = upload_csv_parser.parse_args()
        file = args.get('file')
        bank = args.get('bank')
        account_id = args.get('account_id')
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

    @ns.response(HTTPStatus.OK, 'OK', models['OK'])
    @ns.expect(upload_id_model, validate=True)
    @ns.doc(
        description="Delete an uploaded CSV file of transactions. This will delete any transactions that were created from the upload.")
    @require_auth(ns=ns)
    def delete(self):
        """Delete an uploaded CSV file of transactions."""
        uow = SqlAlchemyUnitOfWork(SessionLocal)
        data = request.get_json()
        delete_upload(uow=uow, user=g.current_user, upload_id=data['id'])
        return OK_RESPONSE


@ns.route('/map')
class TransactionMap(Resource):

    @ns.response(HTTPStatus.OK, 'OK', models['OK'])
    @ns.expect(transaction_map_model, validate=True)
    @ns.doc(
        description="Get a list of transactions with latitude and longitude for mapping. Only transactions with valid latitude and longitude will be returned.")
    @require_auth(ns=ns)
    def post(self):
        """Update an existing transaction's latitude and longitude."""
        uow = SqlAlchemyUnitOfWork(SessionLocal)
        data = request.get_json()

        update_transaction_locations(uow=uow, user=g.current_user, transaction_id=data['id'], latitude=data['latitude'],
                                     longitude=data['longitude'])

        return OK_RESPONSE
