from flask import request
from flask_restx import Resource
from FlaskApp.search.services import get_transactions,get_user_from_token

class Search(Resource):
    def get(self):
        token = request.cookies.get('auth_token')
        start_date=request.args.get('startDate',None)
        end_date = request.args.get('endDate',None)

        e, userid = get_user_from_token(token)
        if e:
            return {'error': e}, 500
        e, res = get_transactions(userid, start_date, end_date)
        if e:
            return {'error': str(e)}, 500
        return {"data":res}, 200
    
    def post(self):
        ...
    def put(self):
        ...
    def delete(self):
        ...