from flask import Flask, request, jsonify, Response, make_response
from flask_restx import Api, Resource
from werkzeug.exceptions import HTTPException
import os, jwt, datetime, bcrypt, sqlite3
from dotenv import load_dotenv
from google.oauth2 import id_token
from google.auth.transport import requests


app = Flask(__name__)
api = Api(app)
load_dotenv()
app.config['SECURE_KEY'] = os.getenv('SECURE_KEY')
app.config['GOOGLE_CLIENT_ID'] = os.getenv('GOOGLE_CLIENT_ID')

def get_db():
    database = r'FlaskApp\spendly.db'
    db = sqlite3.connect(database)
    return db.cursor()

@api.route('/user')
class User(Resource):

    def get(self, email):
        ...
    
    def post(self):
        try:
            curr = get_db()
            data = request.get_json()
            curr.execute("insert into User(email, password) VALUES (?,?)",(data['email'],data['password']))
            curr.connection.commit()
            return {}, 200
        
        except HTTPException as e:
            return {'error': str(e)}, e.code
        except Exception as e:
            return  {'error': str(e)}, 500
    def put(self):
        ...
    def delete(self):
        ...

@api.route('/secure', '/secure/<string:email>')
class Secure(Resource):
    def create_auth_token(self, verified, userID):
        if verified:
            payload = {
                    'userID':userID,
                    'exp': (datetime.datetime.now() + datetime.timedelta(hours=1)).timestamp()
                }

            token = jwt.encode(payload, app.config['SECURE_KEY'], algorithm='HS256')

            response = make_response({'success': True}, 200)
            response.set_cookie(
                'auth_token',
                token,
                max_age=3600,
                httponly=True,
                secure=True,
                samesite='Strict'
            )
            
            return response
        else:
            return {'error': 'Invalid credentials'}, 401   

    def get(self, email):
        try:
            curr = get_db()
            curr.execute("select userID from User where email=?", (email,))
            return {'isStored':bool(curr.fetchone())}, 200
        
        except HTTPException as e:
            return {'error': str(e)}, e.code
        except Exception as e:
            return  {'error': str(e)}, 500

    
    def post(self):
        try:
            curr = get_db()
            data = request.get_json()
            if data['type'] == 'cred':
                # Google login conincides with User Resource as Secure resource handles login/create for google

                cred = data['credential']
                id_info = id_token.verify_oauth2_token(cred, requests.Request(), app.config['GOOGLE_CLIENT_ID'])

                if id_info['aud'] != app.config['GOOGLE_CLIENT_ID']:
                    raise ValueError('Could not verify audience.')
                else:
                    verified=True

                curr.execute("select userID from User where googleID=?", (id_info['sub'],))
                if not curr.fetchone():
                    curr.execute("insert into User(googleEmail, name, googleID, googleImage) VALUES (?,?,?,?)", (id_info['email'], id_info['name'], id_info['sub'], id_info['picture']))
                    curr.connection.commit()
                    curr.execute("select userID from User where googleID=?", (id_info['sub'],))
                userID = curr.fetchone()[0]
                
            else:
                curr.execute("select userID,password from User where email=?", (data['email'],))
                db_data = curr.fetchone()
                hashed_password = db_data[1]
                verified = bcrypt.checkpw(data['password'].encode('utf-8'), hashed_password.encode('utf-8'))
                userID = db_data[0]

            return self.create_auth_token(verified, userID)
        
        except HTTPException as e:
            return {'error': str(e)}, e.code
        except Exception as e:
            return  {'error': str(e)}, 500
    def put(self):
        ...
    def delete(self):
        ...

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')
