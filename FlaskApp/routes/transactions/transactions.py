# TODO: Refactor this file to work with new database structure and akahu integration.
from flask import request
from flask_restx import Resource
from FlaskApp.serv.transactions.services import get_user_from_token, get_transactions, upload_csv, update_category, delete_transaction, get_uploads_by_id, delete_upload
import json

class Transaction(Resource):
    def get(self, count=0, categoryID=None, date=None):
        token = request.cookies.get('auth_token')
        e, userid = get_user_from_token(token)
        if e:
            return {'error': str(e)}, 500
        if 'mass_delete' in request.path:
            e, res = get_uploads_by_id(userid)
            if e:
                return {'error': str(e)}, 500
            return {"data":res}, 200
        e, res = get_transactions(userid, count, categoryID, date)
        if e:
            return {'error': str(e)}, 500
        return {"data":res}, 200

    def post(self):
        token = request.cookies.get('auth_token')
        e, userId = get_user_from_token(token)
        if e:
            return {'error': str(e)}, 500
        file = request.files['file']
        raw_data = request.form.get('data')
        if raw_data is None:
            return {"error": "Missing data field"}, 400
        data = json.loads(raw_data)
        if 'file' not in request.files:
            return {'error': 'No file part'}, 400
        if file.filename == '':
            return {'error': 'No selected file'}, 400
        e = upload_csv(file, userId, data['bank'])
        if e:
            return {'error': str(e)}, 500
        return {},200

    def put(self):
        token = request.cookies.get('auth_token')
        e, _ = get_user_from_token(token)
        if e:
            return {'error': str(e)}, 500
        data = request.get_json()
        e = update_category(data['transactionID'], data['categoryID'])
        if e:
            return {'error': str(e)}, 500
        return {}, 200

    def delete(self):
        token = request.cookies.get('auth_token')
        e, _ = get_user_from_token(token)
        data = request.get_json()
        if 'mass_delete' in request.path:
            e=delete_upload(data['uploadID'])
        else:
            e=delete_transaction(data['transactionID'])
        if e:
            return {'error': str(e)}, 500
        return {}, 200

