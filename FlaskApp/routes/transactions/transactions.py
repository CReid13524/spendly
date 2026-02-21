import datetime
import enum
from http import HTTPStatus
import re

from flask import request, g
from flask_restx import Resource, Namespace, fields, reqparse

from FlaskApp.infra.db import SessionLocal
from FlaskApp.infra.exceptions import ValidationError
from FlaskApp.infra.models import NullableFloat, NullableString, parse_bool, parse_bool_or_other
from FlaskApp.domainmodel.transaction import TransactionType
from FlaskApp.infra.services import CREATED_RESPONSE, OK_RESPONSE, make_ok_response, require_auth, models, validate_uuid
from FlaskApp.infra.unit_of_work import SqlAlchemyUnitOfWork
from FlaskApp.routes.transactions.presentation import transaction_domain_to_json
from FlaskApp.routes.transactions.services import create_transaction, delete_transaction, \
    get_transactions, update_transaction, patch_transaction, update_transaction_locations

ns = Namespace('transactions', description='Operations related to transactions')

class SupportedSort(fields.String, enum.Enum):
    DATE = 'date'
    DATE_DESC = '-date'
    AMOUNT = 'amount'
    AMOUNT_DESC = '-amount'
    CREATED = 'created'
    CREATED_DESC = '-created'

# region Transaction Models and Parsers
transaction_item_model = ns.model('TransactionItem', {
    'id': fields.String(readOnly=True, description='The unique identifier of a transaction',
                        example="a1b2c3d4-e5f6-a1b2-c3d4-e5f6a1b2c3d4"),
    'amount': fields.String(required=True, description='Transaction amount', example='100.50'),
    'date': fields.Date(required=True, description='Transaction date', example="2024-01-01"),
    'description': fields.String(required=True, description='Transaction description', example="Grocery shopping"),
    'balance': NullableString(required=False, description='Account balance after the transaction', example='1500.75'),
    'pending': fields.Boolean(required=True, description='Indicates if the transaction is pending', example=False),
    'type': NullableString(required=True, description='Transaction type', example="VISA PURCHASE", enum=[e.value for e in TransactionType]),
    'status': fields.String(required=True, description='Transaction status', example="active"),
    'created': fields.DateTime(required=True, description='Timestamp when the transaction was created',
                               example="2024-01-01T12:00:00Z"),
    'latitude': NullableFloat(required=False, description='Latitude of the transaction location', example=-36.848378776),
    'longitude': NullableFloat(required=False, description='Longitude of the transaction location',
                               example=174.764381777),
    'category_id': NullableString(required=False, description='ID of the associated category',
                                  example="a1b2c3d4-e5f6-a1b2-c3d4-e5f6a1b2c3d4"),
    'account_id': fields.String(required=True, description='ID of the associated account',
                                example="a1b2c3d4-e5f6-a1b2-c3d4-e5f6a1b2c3d4"),
    'merchant_id': NullableString(required=False, description='ID of the associated merchant',
                                  example="a1b2c3d4-e5f6-a1b2-c3d4-e5f6a1b2c3d4"),
})

editable_transaction_item_model = ns.model('EditableTransactionItem', {
    'amount': fields.String(required=True, description='Transaction amount', example='100.50'),
    'date': fields.Date(required=True, description='Transaction date', example="2024-01-01"),
    'description': fields.String(required=True, description='Transaction description', example="Grocery shopping"),
    'balance': NullableString(required=True, description='Account balance after the transaction', example='1500.75'),
    'pending': fields.Boolean(required=True, description='Indicates if the transaction is pending', example=False),
    'type': NullableString(required=True, description='Transaction type', example="VISA PURCHASE", enum=[e.value for e in TransactionType]),
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

def validate_transaction_editable_fields(data):
    validate_uuid(data['category_id'], "category_id")
    validate_uuid(data['account_id'], "account_id")
    validate_uuid(data['merchant_id'], "merchant_id")
    if data['type'] not in TransactionType._value2member_map_:
        raise ValidationError(f"Invalid transaction type. Valid types: {[e.value for e in TransactionType]}")
    if data['pending'] not in [True, False]:
        raise ValidationError("Invalid pending value. Must be a boolean.")
    if data['status'] not in ['active', 'deleted']:
        raise ValidationError("Invalid status value. Must be 'active' or 'deleted'.")
    if data['date']:
        try:
            datetime.fromisoformat(data['date'])
        except ValueError:
            raise ValidationError("Invalid date format. Must be ISO 8601 format.")
    if not isinstance(data['latitude'], (float, int)) or not -90 <= data['latitude'] <= 90:
        raise ValidationError("Invalid latitude value. Must be a number between -90 and 90. Decimal values should be used for coordinates.")
    if not isinstance(data['longitude'], (float, int)) or not -180 <= data['longitude'] <= 180:
        raise ValidationError("Invalid longitude value. Must be a number between -180 and 180. Decimal values should be used for coordinates.")
    if not re.match(r'^\d+(\.\d{1,2})?$', data['amount']):
        raise ValidationError("Invalid amount format. Must be a valid decimal number with up to 2 decimal places.")
    if data['balance'] is not None and not re.match(r'^\d+(\.\d{1,2})?$', data['balance']):
        raise ValidationError("Invalid balance format. Must be a valid decimal number with up to 2 decimal places.")
    if len(data['description']) > 255:
        raise ValidationError("Description is too long. Maximum length is 255 characters.")

transaction_patch_model = ns.model('PatchTransaction', {
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

# Parser for GET /transactions

get_transactions_parser = reqparse.RequestParser()
get_transactions_parser.add_argument('start_date', type=str, required=False,
                                     help='Start date for filtering transactions (ISO 8601 format)')
get_transactions_parser.add_argument('end_date', type=str, required=False,
                                     help='End date for filtering transactions (ISO 8601 format)')
get_transactions_parser.add_argument('search', type=str, required=False,
                                     help='Search term to filter transactions by description. Case-insensitive substring match.')
get_transactions_parser.add_argument('type', type=str, required=False, choices=[e.value for e in TransactionType],
                                     help='Filter transactions by type. Case-insensitive exact match.')
get_transactions_parser.add_argument('pending', type=parse_bool, choices=[True, False], required=False,
                                     help='Filter transactions by pending status. Boolean.')
get_transactions_parser.add_argument('status', type=str, required=False, default='active',
                                     choices=['active', 'deleted'], help="Filter transactions by status.")
get_transactions_parser.add_argument('category_id', type=lambda x: parse_bool_or_other(x, str), required=False,
                                     help='Category ID for filtering transactions. Boolean indicates existence filter.')
get_transactions_parser.add_argument('account_id', type=str, required=False,
                                     help='Account ID for filtering transactions.')
get_transactions_parser.add_argument('merchant_id', type=lambda x: parse_bool_or_other(x, str), required=False,
                                     help='Merchant ID for filtering transactions. Boolean indicates existence filter.')
get_transactions_parser.add_argument('start_amount', type=str, required=False,
                                     help='Minimum amount for filtering transactions.')
get_transactions_parser.add_argument('end_amount', type=str, required=False,
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
    @ns.response(HTTPStatus.BAD_REQUEST, 'Validation Error', models['BadRequest'])
    @ns.expect(get_transactions_parser, validate=True)
    @ns.doc(
        description="Get a list of transactions with optional filters. By default, only active transactions are returned in date descending order. All filters are optional and can be combined. Pagination and sorting are supported.")
    @require_auth(ns=ns)
    def get(self):
        """Get transactions with optional filters."""
        uow = SqlAlchemyUnitOfWork(SessionLocal)
        args = get_transactions_parser.parse_args()
        filters = {k: v for k, v in args.items() if v is not None}

        # Validation for filters
        try:
            if 'start_date' in filters:
                filters['start_date'] = datetime.fromisoformat(filters['start_date'])
            if 'end_date' in filters:
                filters['end_date'] = datetime.fromisoformat(filters['end_date'])
        except ValueError:
            raise ValidationError(f"Invalid date format. Dates must be in ISO 8601 format.")
        if 'start_amount' in filters and not re.match(r'^\d+(\.\d{1,2})?$', filters['start_amount']):
            raise ValidationError("Invalid start_amount format. Must be a valid decimal number with up to 2 decimal places.")
        if 'end_amount' in filters and not re.match(r'^\d+(\.\d{1,2})?$', filters['end_amount']):
            raise ValidationError("Invalid end_amount format. Must be a valid decimal number with up to 2 decimal places.")
        if 'start_lat' in filters:
            val=filters['start_lat']
            if isinstance(val, (float, int)):
                if not -90 <= val <= 90:
                    raise ValidationError("Invalid start_lat value. Must be a number between -90 and 90. Decimal values should be used for coordinates.")
            elif isinstance(val, (bool)):
                raise ValidationError("Invalid start_lat value. May be a float, int, or boolean for latitude existence filter.")
        if 'end_lat' in filters and (not isinstance(filters['end_lat'], (float, int)) or not -90 <= filters['end_lat'] <= 90):
            raise ValidationError("Invalid end_lat value. Must be a number between -90 and 90. Decimal values should be used for coordinates.")
        if 'start_lng' in filters:
            val=filters['start_lng']
            if isinstance(val, (float, int)):
                if not -180 <= val <= 180:
                    raise ValidationError("Invalid start_lng value. Must be a number between -180 and 180. Decimal values should be used for coordinates.")
            elif isinstance(val, (bool)):
                raise ValidationError("Invalid start_lng value. May be a float, int, or boolean for longitude existence filter.")
        if 'end_lng' in filters and (not isinstance(filters['end_lng'], (float, int)) or not -180 <= filters['end_lng'] <= 180):
            raise ValidationError("Invalid end_lng value. Must be a number between -180 and 180. Decimal values should be used for coordinates.")


        transactions = get_transactions(uow=uow, user=g.current_user, **filters)
        transactions_json = [transaction_domain_to_json(transaction) for transaction in transactions]
        return make_ok_response(transactions=transactions_json)

    @ns.response(HTTPStatus.CREATED, 'OK', models['OK'])
    @ns.response(HTTPStatus.BAD_REQUEST, 'Validation Error', models['BadRequest'])
    @ns.expect(editable_transaction_item_model, validate=True)
    @ns.doc(
        description="Create a new transaction. All fields are required. If the transaction is not associated with a category or merchant, set category_id or merchant_id to null.")
    @require_auth(ns=ns)
    def post(self):
        """Create a new transaction."""

        # Validation
        data = request.get_json()
        validate_transaction_editable_fields(data)

        uow = SqlAlchemyUnitOfWork(SessionLocal)
        create_transaction(uow=uow, user=g.current_user, **data)
        return CREATED_RESPONSE


@ns.route('/<string:transaction_id>')
class TransactionByID(Resource):

    @ns.response(HTTPStatus.OK, 'OK', models['OK'])
    @ns.response(HTTPStatus.BAD_REQUEST, 'Validation Error', models['BadRequest'])
    @ns.expect(editable_transaction_item_model, validate=True)
    @ns.param('transaction_id', description='The unique identifier of the transaction', example="a1b2c3d4-e5f6-a1b2-c3d4-e5f6a1b2c3d4")
    @ns.doc(description="Update an existing transaction. All fields are required, even if not being updated. Use the PATCH endpoint to update only category, merchant, or account relationships.")
    @require_auth(ns=ns)
    def put(self, transaction_id):
        """Update an existing transaction."""
        data = request.get_json()

        # Validation
        validate_uuid(transaction_id, "transaction_id")
        validate_transaction_editable_fields(data)

        uow = SqlAlchemyUnitOfWork(SessionLocal)
        update_transaction(uow=uow, user=g.current_user, transaction_id=transaction_id, **data)
        return OK_RESPONSE

    @ns.response(HTTPStatus.OK, 'OK', models['OK'])
    @ns.response(HTTPStatus.BAD_REQUEST, 'Validation Error', models['BadRequest'])
    @ns.param('transaction_id', description='The unique identifier of the transaction', example="a1b2c3d4-e5f6-a1b2-c3d4-e5f6a1b2c3d4")
    @ns.doc(description="Delete an existing transaction. This will set the transaction's status to 'deleted' (soft delete) and it will no longer be returned in the default GET /transactions endpoint.")
    @require_auth(ns=ns)
    def delete(self, transaction_id):
        """Delete an existing transaction."""

        # Validation
        validate_uuid(transaction_id, "transaction_id")

        uow = SqlAlchemyUnitOfWork(SessionLocal)
        delete_transaction(uow=uow, user=g.current_user, transaction_id=transaction_id)
        return OK_RESPONSE

    @ns.response(HTTPStatus.OK, 'OK', models['OK'])
    @ns.response(HTTPStatus.BAD_REQUEST, 'Validation Error', models['BadRequest'])
    @ns.expect(transaction_patch_model, validate=True)
    @ns.param('transaction_id', description='The unique identifier of the transaction', example="a1b2c3d4-e5f6-a1b2-c3d4-e5f6a1b2c3d4")
    @ns.doc(
        description="Update the category, merchant, or account of an existing transaction. This is intended for updating relationships only, use the PUT endpoint to update other transaction fields.")
    @require_auth(ns=ns)
    def patch(self, transaction_id):
        """Update category, merchant, or account of an existing transaction."""
        data = request.get_json()

        # Validation
        validate_uuid(transaction_id, "transaction_id")
        if 'category_id' in data:
            validate_uuid(data['category_id'], "category_id")
        if 'account_id' in data:
            validate_uuid(data['account_id'], "account_id")
        if 'merchant_id' in data:
            validate_uuid(data['merchant_id'], "merchant_id")

        uow = SqlAlchemyUnitOfWork(SessionLocal)
        patch_transaction(uow=uow, user=g.current_user, transaction_id=transaction_id, **data)
        return OK_RESPONSE


@ns.route('/<string:transaction_id>/map')
class TransactionMap(Resource):

    @ns.response(HTTPStatus.OK, 'OK', models['OK'])
    @ns.response(HTTPStatus.BAD_REQUEST, 'Validation Error', models['BadRequest'])
    @ns.expect(transaction_map_model, validate=True)
    @ns.param('transaction_id', description='The unique identifier of the transaction', example="a1b2c3d4-e5f6-a1b2-c3d4-e5f6a1b2c3d4")
    @ns.doc(
        description="Get a list of transactions with latitude and longitude for mapping. Only transactions with valid latitude and longitude will be returned.")
    @require_auth(ns=ns)
    def post(self, transaction_id):
        """Update an existing transaction's latitude and longitude."""
        data = request.get_json()

        # Validation
        validate_uuid(transaction_id, "transaction_id")

        uow = SqlAlchemyUnitOfWork(SessionLocal)
        update_transaction_locations(uow=uow, user=g.current_user, transaction_id=transaction_id, latitude=data['latitude'],
                                     longitude=data['longitude'])

        return OK_RESPONSE
