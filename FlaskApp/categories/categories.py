from flask import request
from flask_restx import Resource
from FlaskApp.categories.services import get_user_from_token, get_basic_categories, get_advanced_categories, create_category, update_category, delete_category

class Category(Resource):
    def get(self,advanced=False, date=''):
        advanced = bool(advanced)
        token = request.headers.get('auth_token')
        e, userID = get_user_from_token(token)
        if advanced:
            e, res = get_advanced_categories(date, userID)
        else:
            e, res = get_basic_categories(userID)
        if e:
            return {'error': str(e)}, 500
        return {"data":res}, 200

    def post(self):
        token = request.headers.get('auth_token')
        e, userID = get_user_from_token(token)
        data = request.get_json()
        e = create_category(userID,data['name'],data['color'],data['icon'])
        if e:
            return {'error': str(e)}, 500
        return {}, 200

    def put(self):
        token = request.headers.get('auth_token')
        e, _ = get_user_from_token(token)
        data = request.get_json()
        e =update_category(data['name'],data['color'],data['icon'],data['isIncome'],data['isHidden'],data['isDefault'], data['categoryID'])
        if e:
            return {'error': str(e)}, 500
        return {}, 200

    def delete(self):
        token = request.headers.get('auth_token')
        e, _ = get_user_from_token(token)
        if e:
            return {'error': str(e)}, 500
        data = request.get_json()
        e = delete_category(data['categoryID'])
        if e:
            return {'error': str(e)}, 500
        return {}, 200
