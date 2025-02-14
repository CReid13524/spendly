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

    def get(self):
        try:
            auth_data = get_auth_data()
            if not auth_data[0]['valid']:
                raise auth_data[0]['error']
            else:
                userID = auth_data[0]['user']
            
            curr = get_db()

            curr.execute("""Select email, googleEmail, googleImage, name, dateCreated, googleID
                        From User
                        Where userID=?""",(userID,))
            data = curr.fetchone()

            columns = [column[0] for column in curr.description]  # Get column names
            result = dict(zip(columns, data))
            return {'data':result}, 200
        except Exception as e:
            return  {'error': str(e)}, 500
       
    
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
        try:
            auth_data = get_auth_data()
            if not auth_data[0]['valid']:
                raise auth_data[0]['error']
            else:
                userID = auth_data[0]['user']

            curr = get_db()
            data = request.get_json()

            if data['type'] == 'user':
                curr.execute("select password from User where userID=?", (userID,))
                db_data = curr.fetchone()
                hashed_password = db_data[0]
                verified = bcrypt.checkpw(data['password'].encode('utf-8'), hashed_password.encode('utf-8'))
                
                if not verified:
                    raise Exception("Invalid Password")
                
                curr.execute("""Update User set password=?
                            Where userID=?""",(data['passwordNew'], userID))
                curr.connection.commit()

            else:
                cred = data['credential']['credential']
                
                id_info = id_token.verify_oauth2_token(cred, requests.Request(), app.config['GOOGLE_CLIENT_ID'])
                if id_info['aud'] != app.config['GOOGLE_CLIENT_ID']:
                    raise ValueError('Could not verify audience.')

                curr.execute("select userID,email from User where googleID=?", (id_info['sub'],))
                data = curr.fetchone()

                #Update Existing
                if not data:
                    curr.execute("""Update User set googleEmail=?, name=?, googleID=?, googleImage=?
                                Where userID = ? 
                                """, (userID,id_info['email'], id_info['name'], id_info['sub'], id_info['picture']))
                    curr.connection.commit()
                elif (data[0] and not data[1]) and (data[0] != userID):
                    #Logged into a user and has signed up seperatley with google account
                    raise Exception("Account already exists under Google ID. Please remove this account if you wish to connect with Google.")
                    ...
            
            return {},200
            
        except Exception as e:
            return  {'error': str(e)}, 500
        ...
    def delete(self):
        try:
            auth_data = get_auth_data()
            if not auth_data[0]['valid']:
                raise auth_data[0]['error']
            else:
                userID = auth_data[0]['user']

            curr = get_db()
            data = request.get_json()

            if data['type'] == 'reset':
                curr.execute("PRAGMA foreign_keys = ON")
                curr.execute("""Delete from Upload where userID = ?;
                             Delete from Category where userID=?;""", (userID,userID))
                curr.connection.commit()
            elif data['type'] == 'delete':
                curr.execute("PRAGMA foreign_keys = ON")
                curr.execute("""Delete from User where userID=?""", (userID,))
            return {}, 200

        except Exception as e:
            return  {'error': str(e)}, 500

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

@api.route('/record_data', '/record_data/<int:count>/<string:categoryID>', '/record_data/<int:count>','/record_data_filter/<int:count>/<string:date>','/record_data_mass_delete')
class RecordData(Resource):
    def get(self, count=0, categoryID=None, date=None):
        try:
            auth_data = get_auth_data()
            if not auth_data[0]['valid']:
                raise auth_data[0]['error']
            else:
                userID = auth_data[0]['user']

            curr = get_db()
            if 'mass_delete' in request.path:
                curr.execute("""Select Upload.uploadID, Upload.date, count(TransactionID) count FROM Upload
                                LEFT JOIN TRANSACTIONs on Upload.uploadID = Transactions.uploadID
                                Where Upload.userID = ?
                                Group By Upload.uploadID
                            """, (userID,))
                data = curr.fetchall()

                columns = [column[0] for column in curr.description]  # Get column names
                result = [dict(zip(columns, row)) for row in data]

                return {"data":result}, 200

            hidden_filter = ["LEFT Join Category on Transactions.categoryID = Category.categoryID", "AND (isHidden=0 OR isHidden IS NULL)"]
            category_filter = ''
            if categoryID:
                category_filter = f'AND Transactions.categoryID {'is NULL' if categoryID=='null' else f'= {categoryID}'}'

            date_filter = ''
            if date:
                date_filter = f"AND strftime('%Y-%m', Transactions.date) = '{date}'"
            
            curr.execute(f"""select transactionID, title, Transactions.categoryID, type, details, particulars, code, reference, amount, Transactions.date
                         From Transactions
                         Inner Join Upload on Upload.uploadID = Transactions.uploadID
                         {hidden_filter[0] if not category_filter else ''}
                         Where Upload.userID = ? {category_filter if category_filter else hidden_filter[1]} {date_filter}
                         Order By JULIANDAY(Transactions.date) DESC
                         Limit 50 OFFSET ?""", (userID,count))
            data = curr.fetchall()

            columns = [column[0] for column in curr.description]  # Get column names
            result = [dict(zip(columns, row)) for row in data]

            for x in result:
                x['amount'] = f"{'-$' if x['amount']<0 else '$'}{abs(x['amount']):.2f}"
            
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
            
            data = json.loads(request.form['data'])
       
            if file.filename.lower().endswith('.csv'):
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
            
            # Handle ANZ CSV
            if data['bank'] == 'anz':
                df.rename(columns={
                    'Type': 'type',
                    'Details': 'details',
                    'Particulars': 'particulars',
                    'Code': 'code',
                    'Reference': 'reference',
                    'Amount': 'amount',
                    'Date': 'date'
                }, inplace=True)
                
                df['title'] = df.apply(lambda row: row['code'] if 'Visa' in row['type'] or 'Transfer' in row['type'] else row['details'], axis=1)
                
                df = df.drop(columns=['ForeignCurrencyAmount', 'ConversionCharge'])
                
                #Apply Date Formatting
                df['date'] = pd.to_datetime(df['date'], format='%d/%m/%Y', errors='coerce').dt.strftime('%Y-%m-%d')

            # Handle Kiwibank 'FULL CSV'
            elif data['bank'] == 'kiwibank':
                df.rename(columns={
                    'Source Code (payment type)': 'type',
                    'Memo/Description': 'details',
                    'TP part': 'tp_part',
                    'TP code': 'tp_code',
                    'TP ref': 'tp_ref',
                    'OP ref': 'op_ref',
                    'OP part': 'op_part',
                    'OP code': 'op_code',
                    'Amount': 'amount',
                    'Date': 'date'
                }, inplace=True)
                df['title'] = None
                
                # Combine TP and OP references into a single 'reference' column
                df['reference'] = df.apply(lambda row: f"(TP) {row['tp_ref']} (OP) {row['op_ref']}" if not pd.isna(row['tp_ref']) else '', axis=1)
                df['code'] = df.apply(lambda row: f"(TP) {row['tp_code']} (OP) {row['op_code']}" if not pd.isna(row['tp_code']) else '', axis=1)
                df['particulars'] = df.apply(lambda row: f"(TP) {row['tp_part']} (OP) {row['op_part']}" if not pd.isna(row['tp_part']) else '', axis=1)
                
                # Split 'Memo/Description' column on semicolon into 'details' and 'code'
                df[['title', 'details']] = df['details'].str.split(';', n=1, expand=True)

                    

                df = df.drop(columns=['Account number', 'tp_part', 'tp_code', 'tp_ref', 'op_ref', 'op_part', 'op_code', 'OP name', 'OP Bank Account Number', 'Amount (credit)', 'Amount (debit)', 'Balance'])

                #Apply Date Formatting
                df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y', errors='coerce').dt.strftime('%Y-%m-%d')

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

            if 'mass_delete' in request.path:
                curr.execute("PRAGMA foreign_keys = ON")
                curr.execute("""Delete from Upload
                            Where uploadID=?;
                            """, (data['uploadID'],))
                curr.connection.commit()
                return {}, 200

            curr.execute("""Delete from Transactions
                            Where transactionID = ?""",(data['transactionID'],))

            curr.connection.commit()

            return {}, 200
        except Exception as e:
            return {'error': str(e)}, 500
           

@api.route('/categories','/categories/<string:advanced>','/categories/<string:advanced>/<string:date>')
class Categories(Resource):
    def get(self,advanced=False, date=''):
        try:
            advanced = bool(advanced)
            auth_data = get_auth_data()
            if not auth_data[0]['valid']:
                raise auth_data[0]['error']
            else:
                userID = auth_data[0]['user']

            curr = get_db()
            if advanced:
                date_filter = ''
                if date:
                    date_filter = f"Where strftime('%Y-%m', Transactions.date) = '{date}'"

                curr.execute(f"""with transData as (
                                    Select Category.categoryID, IFNULL(SUM(amount),0.0) amount
                                    from Category
                                    LEFT JOIN Transactions on Transactions.categoryID = Category.categoryID
                                    {date_filter}
                                    Group by Category.categoryID
                                )

                                Select  Category.categoryID, name, colour, icon, transData.amount, isIncome, isHidden, isDefault from Category
                                JOIN transData on transData.categoryID = Category.categoryID
                                Where userID=?""",(userID,))
            else:
                curr.execute("""Select  categoryID, name, colour, icon from Category
                                where userID=?""", (userID,))
            data = curr.fetchall()

            columns = [column[0] for column in curr.description]
            result = [dict(zip(columns, row)) for row in data]
            

            if advanced:
                for x in result:
                    x['amount'] = f"{'-$' if x['amount']<0 else '$'}{abs(x['amount']):.2f}"
                    x['isIncome'] = bool(x['isIncome'])

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
            curr.execute("""Update Category set name=?, colour=?, icon=?, isIncome=?, isHidden=?, isDefault=?
                            Where categoryID = ?""",
                         (data['name'],data['color'],data['icon'],data['isIncome'],data['isHidden'],data['isDefault'], data['categoryID']))
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
            curr.execute("PRAGMA foreign_keys = ON")
            curr.execute("""Delete from Category 
                        Where categoryID=?;""", (data['categoryID'],))
            curr.connection.commit()

            return {}, 200
        except Exception as e:
            return {'error': str(e)}, 500


if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')
