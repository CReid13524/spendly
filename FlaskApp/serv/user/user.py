from flask import request, make_response
from flask_restx import Resource
from FlaskApp.serv.user.services import get_user_data, create_new_user, login_exisiting_user, get_user_from_token, reset_user_account, delete_user_account
from werkzeug.exceptions import HTTPException

class User(Resource):

    def get(self):
        token = request.cookies.get('auth_token')
        e, userID = get_user_from_token(token)
        if e:
            return  {'error': str(e)}, 500
        e, data = get_user_data(userID)
        if e:
            return  {'error': str(e)}, 500
        return {'data': data}, 200

    def post(self):
        try:
            data = request.get_json()
        except HTTPException as e:
            return {'error': str(e)}, e.code
        e = create_new_user(data['email'],data['password'])
        if e:
            return  {'error': str(e)}, 500
        return {}, 200

    def put(self):
        token = request.cookies.get('auth_token')
        e, userID = get_user_from_token(token)
        if e:
            return  {'error': str(e)}, 500
        e = login_exisiting_user(userID, request)
        if e :
            return  {'error': str(e)}, 500
        return {}, 200

    def delete(self):
        token = request.cookies.get('auth_token')
        e, userID = get_user_from_token(token)
        if e:
            return  {'error': str(e)}, 500
        data = request.get_json()
        response = make_response({}, 200)
        if data['type'] == 'reset':
            reset_user_account()
        elif data['type'] == 'delete':
            delete_user_account()
            response.set_cookie(
                'auth_token',
                "",
                max_age=0,
                httponly=True,
                secure=False,
                samesite='Strict'
            )
        return response
