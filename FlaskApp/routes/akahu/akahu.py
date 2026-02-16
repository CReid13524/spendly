from http import HTTPStatus

from flask import request, g
from flask_restx import Resource, Namespace, fields

from FlaskApp.infra.db import SessionLocal
from FlaskApp.infra.services import OK_RESPONSE, models
from FlaskApp.infra.services import require_auth
from FlaskApp.infra.unit_of_work import SqlAlchemyUnitOfWork
from FlaskApp.routes.akahu.services import sync_akahu, connect_akahu

ns = Namespace('akahu', description='Akahu integration endpoints')

# region Models
akahu_connect_model = ns.model('AkahuConnect', {
    'akahu_user_id': fields.String(required=True, description='Akahu user ID',
                                   example='user_token_123'),
    'akahu_app_id': fields.String(required=True, description='Akahu app ID',
                                  example='app_token_123'),
})


# endregion


@ns.route('')
class AkahuResource(Resource):
    @require_auth(ns=ns)
    @ns.doc(description="Sync Akahu data with Spendly")
    @ns.response(HTTPStatus.OK, 'OK', models['OK'])
    @ns.param('full_sync', 'Whether to perform a full sync. Default is false, which only syncs latest 50 transactions.',
              "query", default="False", type="boolean")
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
