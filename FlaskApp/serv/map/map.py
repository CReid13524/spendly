from flask import request
from flask_restx import Resource
from FlaskApp.serv.map.services import updateTransactionCoordinates, get_user_from_token,deleteTransactionCoordinates


class Map(Resource):

    def post(self):
        token = request.cookies.get('auth_token')
        e, _ = get_user_from_token(token)
        if e:
            return {'error': e}, 500
        data = request.get_json()
        e = updateTransactionCoordinates(data['transactionID'], data['longitude'], data['latitude'])
        if e:
            return {'error': str(e)}, 500
        return {}, 200

    def delete(self):
        token = request.cookies.get('auth_token')
        e, _ = get_user_from_token(token)
        if e:
            return {'error': e}, 500
        data = request.get_json()
        e, res = deleteTransactionCoordinates(data['transactionID'])
        if e:
            return {'error': str(e)}, 500
        return {}, 200