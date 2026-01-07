import datetime
import jwt
from flask import make_response
from flask import current_app
from FlaskApp.serv.services import get_db, get_user_from_token, get_auth_data
from google.oauth2 import id_token
import bcrypt

def create_auth_token(verified, userID):
    if verified:
        curr = get_db()
        curr.execute('Update User Set lastLogin = CURRENT_TIMESTAMP where userID=?',(userID,))
        curr.connection.commit()
        payload = {
                'userID':userID,
                'exp': (datetime.datetime.now() + datetime.timedelta(hours=1)).timestamp()
            }
        token = jwt.encode(payload, current_app.config['SECURE_KEY'], algorithm='HS256')
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
    
def check_user_exists(email):
    try:
        curr = get_db()
        curr.execute("select userID from User where email=? and status='active'", (email,))
        res = curr.fetchone()
        return None, res
    except Exception as e:
        return e, None
    
def login_with_google(cred, request):
    # Google login conincides with User Resource as Secure resource handles login/create for google
    try:
        curr = get_db()
        id_info = id_token.verify_oauth2_token(cred, request, current_app.config['GOOGLE_CLIENT_ID'])
        if id_info['aud'] != current_app.config['GOOGLE_CLIENT_ID']:
            print(id_info['aud'], current_app.config['GOOGLE_CLIENT_ID'])
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
        return None, create_auth_token(verified, userID)
    except Exception as e:
        return e, None
    finally:
        curr.connection.close()

def login_with_details(email,password):
    try:
        curr = get_db()
        curr.execute("select userID,password from User where email=?", (email,))
        db_data = curr.fetchone()
        hashed_password = db_data[1]
        verified = bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
        userID = db_data[0]
        return None, create_auth_token(verified, userID)
    except Exception as e:
        return e, None
    finally:
        curr.connection.close()