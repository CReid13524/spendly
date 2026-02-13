from dataclasses import fields
from flask import request, make_response
from flask_restx import Resource, Namespace, fields
from FlaskApp.infra.db import SessionLocal
from FlaskApp.infra.unit_of_work import SqlAlchemyUnitOfWork
from FlaskApp.routes.user.services import create_new_user, ValidationError
from http import HTTPStatus

ns = Namespace("user", description="User management endpoints")

new_user_model = ns.model('NewUser', {
    'email': fields.String(required=True, description='User email', example='me@example.com'),
    'password': fields.String(required=True, description='User password', example='example'),
    'name': fields.String(required=True, description='User name', example='John Doe'),
})

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
    @ns.response(201, 'User created successfully')
    @ns.response(400, 'Validation error')
    def post(self):
        """
        Create a new user with email and password
        """
        payload = request.get_json()
        uow = SqlAlchemyUnitOfWork(SessionLocal)

        create_new_user(uow=uow, email=payload['email'], password=payload['password'], name=payload['name'])
        return {"success": True}, HTTPStatus.CREATED

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
