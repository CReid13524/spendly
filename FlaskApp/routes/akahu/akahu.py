from http import HTTPStatus

from flask import request
from flask_restx import Resource, Namespace, fields

from FlaskApp.infra.db import SessionLocal
from FlaskApp.infra.services import require_auth
from FlaskApp.infra.unit_of_work import SqlAlchemyUnitOfWork
from FlaskApp.routes.akahu.services import sync_akahu, connect_akahu

ns = Namespace('akahu', description='Akahu integration endpoints')

akahu_connect_model = ns.model('AkahuConnect', {
    'akahu_user_id': fields.String(required=True, description='Akahu user ID',
                                   example='user_token_123'),
    'akahu_app_id': fields.String(required=True, description='Akahu app ID',
                                  example='app_token_123'),
})


@ns.route('')
class AkahuResource(Resource):
    @require_auth
    @ns.doc(description="Sync Akahu data with Spendly")
    @ns.response(200, 'OK')
    @ns.response(401, 'Authentication required')
    @ns.param('full_sync', 'Whether to perform a full sync. Default is false, which only syncs latest 50 transactions.',
              "query", default="False", type="boolean")
    def get(self):
        """
        Download latest data from Akahu and update Spendly accounts and transactions
        """
        uow = SqlAlchemyUnitOfWork(SessionLocal)
        request_args = request.args
        full_sync = request_args.get('full_sync', 'False').lower() == 'true'
        sync_akahu(uow=uow, full_sync=full_sync)
        try:

            return {"success": True}, HTTPStatus.OK
        except Exception as e:
            return {'success': False, 'message': str(e)}, HTTPStatus.INTERNAL_SERVER_ERROR

    @require_auth
    @ns.doc(description="Connect Akahu account to Spendly")
    @ns.response(200, 'OK')
    @ns.response(400, 'Validation error')
    @ns.response(401, 'Authentication required')
    @ns.expect(akahu_connect_model, validate=True)
    def post(self):
        """
        Connect Akahu account to Spendly by saving the Akahu credentials
        """
        payload = request.get_json()
        bearer = payload["akahu_user_id"]
        app_id = payload["akahu_app_id"]
        uow = SqlAlchemyUnitOfWork(SessionLocal)
        try:
            connect_akahu(
                bearer_token=bearer,
                app_id=app_id,
                uow=uow,
            )
            return {"success": True}, HTTPStatus.OK
        except ValueError as ve:
            return {'success': False, 'message': str(ve)}, HTTPStatus.BAD_REQUEST
        except Exception as e:
            return {'success': False, 'message': str(e)}, HTTPStatus.INTERNAL_SERVER_ERROR
