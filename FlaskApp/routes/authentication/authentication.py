from flask import request
from flask_restx import Namespace, Resource, fields
from FlaskApp.routes.authentication.services import login_with_google, login_with_details, InvalidCredentials
from FlaskApp.infra.db import SessionLocal
from FlaskApp.infra.unit_of_work import SqlAlchemyUnitOfWork
from http import HTTPStatus

ns = Namespace('authentication', description='Authentication endpoints')

auth_model = ns.model('Auth', {
    'email': fields.String(required=True, description='email', example='me@example.com'),
    'password': fields.String(required=True, description='password', example='example'),
})

google_auth_model = ns.model('GoogleAuth', {
    'credential': fields.String(required=True, description='Google token', example='not_a_valid_token'),
})
@ns.route('')
class Authentication(Resource):

    @ns.expect(auth_model, validate=True)
    @ns.doc(description="Authenticate by email/password")
    @ns.response(200, 'OK')
    @ns.response(401, 'Invalid credentials')
    @ns.response(400, 'Validation error')
    def post(self):
        """
        Generate auth token for exsiting user. Returns auth token
        """
        payload = request.get_json()
        uow = SqlAlchemyUnitOfWork(SessionLocal)
        try:

            response = login_with_details(
                uow=uow,
                email=payload['email'],
                password=payload['password']
            )

            return response

        except InvalidCredentials as e:
            return {'success': False, 'message': str(e)}, HTTPStatus.UNAUTHORIZED

        except Exception as e:
            return {'success': False, 'message': str(e)}, HTTPStatus.INTERNAL_SERVER_ERROR

    # TODO: add polling endpoint
    # def put(self):
    #     token = request.cookies.get('auth_token')
    #     return get_auth_data(token)

@ns.route('/google')
class GoogleAuthentication(Resource):
    @ns.expect(google_auth_model, validate=True)
    @ns.doc(description="Authenticate by Google credential")
    @ns.response(200, 'OK')
    @ns.response(401, 'Invalid credentials')
    @ns.response(400, 'Validation error')
    def post(self):
        """
        Create or authenticate user by Google credential. Returns auth token
        """
        payload = request.get_json()
        uow = SqlAlchemyUnitOfWork(SessionLocal)
        try:
            response = login_with_google(
                uow=uow,
                credential=payload['credential'],
                request=request
            )

            return response

        except InvalidCredentials as e:
            return {'success': False, 'message': str(e)}, HTTPStatus.UNAUTHORIZED

        except Exception as e:
            return {'success': False, 'message': str(e)}, HTTPStatus.INTERNAL_SERVER_ERROR


