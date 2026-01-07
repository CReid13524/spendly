from flask import request
from flask_restx import Resource
from FlaskApp.serv.authentication.services import check_user_exists, login_with_google, login_with_details, get_auth_data


class Authentication(Resource):

    def get(self, email):
        e, res = check_user_exists(email)
        if e:
            return  {'error': str(e)}, 500
        return {'isStored':bool(res)}, 200

    def post(self):
        data = request.get_json()
        if data['type'] == 'cred':
            e, token = login_with_google(data['credential'], request)
        else:
            e, token = login_with_details(data['email'], data['password'])
        if e:
            return  {'error': str(e)}, 500
        return token

    def put(self):
        token = request.cookies.get('auth_token')
        return get_auth_data(token)
