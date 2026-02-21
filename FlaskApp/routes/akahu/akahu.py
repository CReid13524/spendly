from http import HTTPStatus

from flask import request, g
from flask_restx import Resource, Namespace, fields

from FlaskApp.infra.db import SessionLocal
from FlaskApp.infra.exceptions import ValidationError
from FlaskApp.infra.services import OK_RESPONSE, make_ok_response, models
from FlaskApp.infra.services import require_auth
from FlaskApp.infra.unit_of_work import SqlAlchemyUnitOfWork
from FlaskApp.routes.akahu.presentation import akahu_account_domain_to_json, compare_akahu_account_domain_to_json
from FlaskApp.routes.akahu.services import sync_akahu, connect_akahu, get_akahu_accounts, balance_akahu_account
from FlaskApp.routes.accounts.accounts import account_item_model
ns = Namespace('akahu', description='Akahu integration endpoints')

# region Models
akahu_connect_model = ns.model('AkahuConnect', {
    'akahu_user_id': fields.String(required=True, description='Akahu user ID',
                                   example='user_token_123'),
    'akahu_app_id': fields.String(required=True, description='Akahu app ID',
                                  example='app_token_123'),
})

akahu_balance_account_model = ns.model('AkahuAccountBalance', {
        'akahu_account_id': fields.String(description="List of Akahu account IDs to refresh. If empty, all accounts will be refreshed.", example="acc_abcdefghijklmnopqrstuvwxy")
    })

akahu_account_item_model = ns.model('AkahuAccount', {
    "id": fields.String(description="Akahu account ID"),
    "authorisation": fields.String(description="Authorization status of the account"),
    "meta": fields.Raw(description="Metadata associated with the account"),
    "connection_id": fields.String(description="ID of the Akahu connection"),
    "connection_type": fields.String(description="Type of the Akahu connection"),
    "refreshed": fields.DateTime(description="Last refreshed timestamp"),
    "refresh_attempt": fields.DateTime(description="Last refresh attempt timestamp"),

    # Similar field to accounts
    "name": fields.String(description="Name of the account", example="My Checking Account"),
    "type": fields.String(description="Type of the account", example="CHECKING"),
    "formatted_account": fields.String(description="Formatted account details", example="12-3456-7890123-00"),
    "currency": fields.String(description="Currency code", example="USD"),
    "current_balance": fields.String(description="Current balance as a string to preserve precision", example="100.50"),
    "available_balance": fields.String(description="Available balance as a string to preserve precision", example="80.00"),
    "status": fields.String(description="Status of the account", example="active"),
    "created": fields.DateTime(description="Account creation timestamp", example="2023-01-01T00:00:00Z"),
    "credit_limit": fields.String(description="Credit limit as a string to preserve precision", example="500.00"),
    "overdrawn": fields.Boolean(description="Whether the account is overdrawn", example=False),
    "connection_name": fields.String(description="Name of the connected institution", example="Bank A"),
    "connection_logo": fields.String(description="URL of the institution's logo", example="https://logo.url/bank_a.png"),
})

akahu_accounts_model = ns.model('AkahuAccounts', {
    'success': fields.Boolean(description="Whether the request was successful"),
    'accounts': fields.List(fields.Nested(akahu_account_item_model), description="List of Akahu accounts")
})

akahu_account_comparison_model = ns.model('AkahuAccountComparison', {
    'success': fields.Boolean(description="Whether the request was successful"),
    'accounts': fields.List(fields.Nested(ns.model('AkahuAccountComparisonItem', {
        'akahu_account': fields.Nested(akahu_account_item_model, description="The Akahu account details"),
        'spendly_account': fields.Nested(account_item_model, description="The corresponding Spendly account details")
    })), description="List of Akahu accounts with their corresponding Spendly accounts")
})

# endregion


@ns.route('')
class AkahuResource(Resource):
    @require_auth(ns=ns)
    @ns.doc(description="Sync Akahu data with Spendly")
    @ns.response(HTTPStatus.OK, 'OK', models['OK'])
    @ns.param('full_sync', 'Whether to perform a full sync. Default is false, which only syncs latest 50 transactions.',
              "query", default=False, type="boolean")
    def get(self):
        """Download latest data from Akahu and update Spendly accounts and transactions"""
        uow = SqlAlchemyUnitOfWork(SessionLocal)
        request_args = request.args
        full_sync = request_args.get('full_sync', 'False').lower() == 'true'
        sync_akahu(uow=uow, full_sync=full_sync, user=g.current_user)
        return OK_RESPONSE

    @require_auth(ns=ns)
    @ns.doc(description="Connect Akahu account to Spendly")
    @ns.response(HTTPStatus.OK, 'OK', models['OK'])
    @ns.response(HTTPStatus.BAD_REQUEST, 'Validation error', models['BadRequest'])
    @ns.expect(akahu_connect_model, validate=True)
    def post(self):
        """Connect Akahu account to Spendly by saving the Akahu credentials"""
        payload = request.get_json()
        bearer = payload["akahu_user_id"]
        app_id = payload["akahu_app_id"]
        uow = SqlAlchemyUnitOfWork(SessionLocal)
        connect_akahu(
            bearer_token=bearer,
            app_id=app_id,
            uow=uow,
            user=g.current_user
        )
        return OK_RESPONSE

@ns.route('/accounts')
class AkahuAccountsResource(Resource):
    @ns.param('compare', 'Whether to compare with existing accounts and only return new accounts. Default is false.',
              "query", default=False, type="boolean")
    @ns.doc(description="Get all accounts linked with Akahu for the authenticated user")
    @ns.response(HTTPStatus.OK, 'OK', akahu_accounts_model)
    @ns.response(f'{HTTPStatus.OK} (compared)', 'OK (compared)', akahu_account_comparison_model)
    @require_auth(ns=ns)
    def get(self):
        """Get all accounts linked with Akahu for the authenticated user"""
        uow = SqlAlchemyUnitOfWork(SessionLocal)
        request_args = request.args
        compare = request_args.get('compare', 'false').lower() == 'true'

        accounts = get_akahu_accounts(uow=uow, user=g.current_user, compare=compare)

        if compare:
            accounts_json = [compare_akahu_account_domain_to_json(ak, ac) for ak, ac in accounts.items()]
        else:
            accounts_json = [akahu_account_domain_to_json(ak) for ak in accounts]
        return make_ok_response(accounts=accounts_json)

    @ns.response(HTTPStatus.OK, 'OK', models['OK'])
    @ns.response(HTTPStatus.BAD_REQUEST, 'Validation error', models['BadRequest'])
    @ns.expect(akahu_balance_account_model, validate=True)
    @ns.doc(description="Balance Akahu account by recalculating the balance based on transactions. This is useful when transactions are added/updated outside of the normal sync process.")
    @require_auth(ns=ns)
    def put(self):
        """Balance Akahu account by recalculating the balance based on transactions. This is useful when transactions are added/updated outside of the normal sync process."""
        uow = SqlAlchemyUnitOfWork(SessionLocal)
        payload = request.get_json()
        akahu_account_id = payload.get("akahu_account_id")
        if not akahu_account_id:
            raise ValidationError("akahu_account_id is required")
        balance_akahu_account(uow=uow, akahu_account_id=akahu_account_id, user=g.current_user)
        return OK_RESPONSE