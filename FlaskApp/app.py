from flask import Flask, request, jsonify, Response, make_response
from flask_restx import Api, Resource
from werkzeug.exceptions import HTTPException
import os, jwt, datetime, bcrypt, sqlite3
from dotenv import load_dotenv
from google.oauth2 import id_token
from google.auth.transport import requests
import pandas as pd
import json


app = Flask(__name__)
api = Api(app)
load_dotenv()
app.config['SECURE_KEY'] = os.getenv('SECURE_KEY')
app.config['GOOGLE_CLIENT_ID'] = os.getenv('GOOGLE_CLIENT_ID')

def get_db():
    database = r'FlaskApp\spendly.db'
    db = sqlite3.connect(database)
    return db.cursor()

def get_auth_data():
        token = request.cookies.get('auth_token')
        if not token:
            return {"valid": False, "error": "Missing token"}, 401
        try:
            decoded = jwt.decode(token, app.config['SECURE_KEY'], algorithms=["HS256"])
            return {"valid": True, "user": decoded["userID"]}, 200
        except jwt.ExpiredSignatureError:
            return {"valid": False, "error": "Token expired"}, 401
        except jwt.InvalidTokenError:
            return {"valid": False, "error": "Invalid token"}, 401

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
                secure=False,
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
                data = curr.fetchone()
                if not data:
                    curr.execute("insert into User(googleEmail, name, googleID, googleImage) VALUES (?,?,?,?)", (id_info['email'], id_info['name'], id_info['sub'], id_info['picture']))
                    curr.connection.commit()
                    curr = get_db()
                    curr.execute("select userID from User where googleID=?", (id_info['sub'],))
                    userID = curr.fetchone()[0]
                else:
                    userID = data[0]
                
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
        return get_auth_data()
    
    def delete(self):
        ...

@api.route('/record_data', '/record_data/<int:count>/<string:categoryID>', '/record_data/<int:count>')
class RecordData(Resource):
    def get(self, count=0, categoryID=None):
        try:
            auth_data = get_auth_data()
            if not auth_data[0]['valid']:
                raise auth_data[0]['error']
            else:
                userID = auth_data[0]['user']

            category_filter = ''
            if categoryID:
                category_filter = f'AND categoryID={categoryID}'

            curr = get_db()
            curr.execute(f"""select transactionID, categoryID, type, details, particulars, code, reference, amount, Transactions.date
                         From Transactions
                         Inner Join Upload on Upload.uploadID = Transactions.uploadID
                         Where userID = ? {category_filter}
                         Order By JULIANDAY(Transactions.date) DESC
                         Limit 50 OFFSET ?""", (userID,count))
            data = curr.fetchall()

            columns = [column[0] for column in curr.description]  # Get column names
            result = [dict(zip(columns, row)) for row in data]

            return {"data":result}, 200
        except Exception as e:
            return {'error': str(e)}, 500

    def post(self):
        try:
            file = request.files['file']
            auth_data = get_auth_data()
            if not auth_data[0]['valid']:
                raise auth_data[0]['error']
            else:
                userID = auth_data[0]['user']

            if 'file' not in request.files:
                return {'error': 'No file part'}, 400
            if file.filename == '':
                return {'error': 'No selected file'}, 400

       
            if file.filename.endswith('.csv'):
                df = pd.read_csv(file)
            elif file.filename.endswith('.xlsx'):
                df = pd.read_excel(file)
            else:
                return {'error': 'Unsupported file format'}, 400
            
            #Get uploadID
            conn = sqlite3.connect(r'FlaskApp/spendly.db')
            curr = conn.cursor()
            curr.execute('insert into Upload(userID) VALUES (?)',(userID,))
            uploadID = curr.lastrowid
            
            #Apply uploadID
            df['uploadID'] = uploadID
            
            #Insert Data
            df.to_sql('Transactions', conn, if_exists='append', index=False)
            conn.commit()

            return {},200

        except Exception as e:
            return {'error': str(e)}, 500
        
    def put(self):
        try:
            auth_data = get_auth_data()
            if not auth_data[0]['valid']:
                raise auth_data[0]['error']

            data = request.get_json()

            curr = get_db()
            curr.execute("""Update Transactions
                            Set categoryID = ?
                            Where transactionID = ?""",(data['categoryID'],data['transactionID']))

            curr.connection.commit()

            return {}, 200
        except Exception as e:
            return {'error': str(e)}, 500
    def delete(self):
        try:
            auth_data = get_auth_data()
            if not auth_data[0]['valid']:
                raise auth_data[0]['error']

            data = request.get_json()

            curr = get_db()
            curr.execute("""Delete from Transactions
                            Where transactionID = ?""",(data['transactionID'],))

            curr.connection.commit()

            return {}, 200
        except Exception as e:
            return {'error': str(e)}, 500
           

@api.route('/categories','/categories/<string:advanced>')
class Categories(Resource):
    def get(self,advanced=False):
        try:
            advanced = bool(advanced)
            auth_data = get_auth_data()
            if not auth_data[0]['valid']:
                raise auth_data[0]['error']
            else:
                userID = auth_data[0]['user']

            curr = get_db()
            if advanced:
                curr.execute("""with transData as (
                                    Select Category.categoryID, IFNULL(SUM(amount),0.0) amount
                                    from Category
                                    LEFT JOIN Transactions on Transactions.categoryID = Category.categoryID
                                    Group by Category.categoryID
                                )

                                Select  Category.categoryID, name, colour, icon, transData.amount from Category
                                JOIN transData on transData.categoryID = Category.categoryID
                                Where userID=?""",(userID,))
            else:
                curr.execute("""Select  categoryID, name, colour, icon from Category
                                where userID=?""", (userID,))
            data = curr.fetchall()

            columns = [column[0] for column in curr.description]
            result = [dict(zip(columns, row)) for row in data]

            return {"data":result}, 200
        except Exception as e:
            return {'error': str(e)}, 500
    def post(self):
        try:
            auth_data = get_auth_data()
            if not auth_data[0]['valid']:
                raise auth_data[0]['error']
            else:
                userID = auth_data[0]['user']
            data = request.get_json()

            curr = get_db()
            curr.execute("Insert into Category(userID, name, colour, icon) VALUES (?,?,?,?)",
                         (userID,data['name'],data['color'],data['icon']))
            curr.connection.commit()

            return {}, 200
        except Exception as e:
            return {'error': str(e)}, 500
    def put(self):
        try:
            auth_data = get_auth_data()
            if not auth_data[0]['valid']:
                raise auth_data[0]['error']
            data = request.get_json()

            curr = get_db()
            curr.execute("""Update Category set name=?, colour=?, icon=?
                            Where categoryID = ?""",
                         (data['name'],data['color'],data['icon'],data['categoryID']))
            curr.connection.commit()

            return {}, 200
        except Exception as e:
            return {'error': str(e)}, 500
    def delete(self):
        try:
            auth_data = get_auth_data()
            if not auth_data[0]['valid']:
                raise auth_data[0]['error']
            data = request.get_json()

            curr = get_db()
            curr.execute("""Delete from Category 
                            Where categoryID=?""", (data['categoryID'],))
            curr.connection.commit()

            return {}, 200
        except Exception as e:
            return {'error': str(e)}, 500


if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')
