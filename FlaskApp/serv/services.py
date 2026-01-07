import sqlite3
import jwt
from flask import current_app

def get_db():
    database = r'FlaskApp/spendly.db'
    db = sqlite3.connect(database)
    return db.cursor()

def get_auth_data(token):

        if not token:
            return {"valid": False, "error": "Missing token"}, 401
        try:
            decoded = jwt.decode(token, current_app.config['SECURE_KEY'], algorithms=["HS256"])
            return {"valid": True, "user": decoded["userID"]}, 200
        except jwt.ExpiredSignatureError:
            return {"valid": False, "error": "Token expired"}, 401
        except jwt.InvalidTokenError:
            return {"valid": False, "error": "Invalid token"}, 401

def get_user_from_token(token):
    try:
        auth_data = get_auth_data(token)
        if not auth_data[0]['valid']:
            raise auth_data[0]['error']
        else:
            userID = auth_data[0]['user']
            return None, userID
    except Exception as e:
        return e, None