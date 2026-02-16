from http import HTTPStatus

from flask import request
from flask_restx import Resource, Namespace, fields

from FlaskApp.infra.db import SessionLocal
from FlaskApp.infra.services import CREATED_RESPONSE, models
from FlaskApp.infra.unit_of_work import SqlAlchemyUnitOfWork
from FlaskApp.routes.user.services import create_new_user

ns = Namespace("user", description="User management endpoints")

# region Models
new_user_model = ns.model('NewUser', {
    'email': fields.String(required=True, description='User email', example='me@example.com'),
    'password': fields.String(required=True, description='User password', example='example'),
    'name': fields.String(required=True, description='User name', example='John Doe'),
})


# endregion


@ns.route('')
class User(Resource):

    #TODO
    # def get(self):
    #     token = request.cookies.get('auth_token')
    #     e, userID = get_user_from_token(token)
    #     if e:
    #         return  {'error': str(e)}, 500
    #     e, data = get_user_data(userID)
    #     if e:
    #         return  {'error': str(e)}, 500
    #     return {'data': data}, 200

    @ns.expect(new_user_model, validate=True)
    @ns.doc(description="Create a new user with email and password")
    @ns.response(HTTPStatus.CREATED, 'User created successfully', models['OK'])
    @ns.response(HTTPStatus.BAD_REQUEST, 'Validation error', models['BadRequest'])
    def post(self):
        """
        Create a new user with email and password
        """
        payload = request.get_json()
        uow = SqlAlchemyUnitOfWork(SessionLocal)

        create_new_user(uow=uow, email=payload['email'], password=payload['password'], name=payload['name'])
        return CREATED_RESPONSE

    # TODO
    # def put(self):
    #     token = request.cookies.get('auth_token')
    #     e, userID = get_user_from_token(token)
    #     if e:
    #         return  {'error': str(e)}, 500
    #     e = login_exisiting_user(userID, request)
    #     if e :
    #         return  {'error': str(e)}, 500
    #     return {}, 200

    # def delete(self):
    #     token = request.cookies.get('auth_token')
    #     e, userID = get_user_from_token(token)
    #     if e:
    #         return  {'error': str(e)}, 500
    #     data = request.get_json()
    #     response = make_response({}, 200)
    #     if data['type'] == 'reset':
    #         reset_user_account()
    #     elif data['type'] == 'delete':
    #         delete_user_account()
    #         response.set_cookie(
    #             'auth_token',
    #             "",
    #             max_age=0,
    #             httponly=True,
    #             secure=False,
    #             samesite='Strict'
    #         )
    #     return response
