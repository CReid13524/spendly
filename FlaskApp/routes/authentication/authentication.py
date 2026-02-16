from http import HTTPStatus

from flask import request
from flask_restx import Namespace, Resource, fields

from FlaskApp.infra.db import SessionLocal
from FlaskApp.infra.services import models
from FlaskApp.infra.unit_of_work import SqlAlchemyUnitOfWork
from FlaskApp.routes.authentication.services import login_with_google, login_with_details

ns = Namespace('authentication', description='Authentication endpoints')

# region Models
auth_model = ns.model('Auth', {
    'email': fields.String(required=True, description='email', example='me@example.com'),
    'password': fields.String(required=True, description='password', example='example'),
})

google_auth_model = ns.model('GoogleAuth', {
    'credential': fields.String(required=True, description='Google token', example='not_a_valid_token'),
})


# endregion


@ns.route('')
class Authentication(Resource):

    @ns.expect(auth_model, validate=True)
    @ns.doc(description="Authenticate by email/password")
    @ns.response(HTTPStatus.OK, 'OK', models['OK'])
    @ns.response(HTTPStatus.BAD_REQUEST, 'Invalid credentials', models['BadRequest'])
    def post(self):
        """Generate auth token for existing user. Returns auth token if successful."""
        payload = request.get_json()
        uow = SqlAlchemyUnitOfWork(SessionLocal)
        response = login_with_details(
            uow=uow,
            email=payload['email'],
            password=payload['password']
        )
        return response

    # TODO: add polling endpoint
    # def put(self):
    #     token = request.cookies.get('auth_token')
    #     return get_auth_data(token)

@ns.route('/google')
class GoogleAuthentication(Resource):
    @ns.expect(google_auth_model, validate=True)
    @ns.doc(description="Authenticate by Google credential")
    @ns.response(HTTPStatus.OK, 'OK', models['OK'])
    @ns.response(HTTPStatus.BAD_REQUEST, 'Validation error', models['BadRequest'])
    def post(self):
        """Create or authenticate user by Google credential. Returns auth token if successful."""
        payload = request.get_json()
        uow = SqlAlchemyUnitOfWork(SessionLocal)
        response = login_with_google(
            uow=uow,
            credential=payload['credential'],
            request=request
        )
        return response
