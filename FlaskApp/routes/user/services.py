from datetime import datetime, timezone
import uuid
import bcrypt
from flask import current_app
from google.oauth2 import id_token
from FlaskApp.domainmodel import User
from FlaskApp.infra.unit_of_work import AbstractUnitOfWork
from FlaskApp.infra.exceptions import ValidationError
# TODO
# def get_user_data(userID):
#     try:
#         curr = get_db()

#         curr.execute("""Select email, googleEmail, googleImage, name, dateCreated, googleID
#                     From User
#                     Where userID=?
#                     AND status == 'active'
#                     """,(userID,))
#         data = curr.fetchone()

#         columns = [column[0] for column in curr.description]  # Get column names
#         result = dict(zip(columns, data))

#         return None, result

#     except Exception as e:
#         return  e, None
#     finally:
#         curr.connection.close()

def create_new_user(uow: AbstractUnitOfWork, email, password, name):
    with uow:
        existing_user = uow.users.get_by_email(email=email)
        if existing_user:
            raise ValidationError("User with this email already exists")
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        user = User(
            user_id=uuid.uuid4(),
            email=email,
            password=hashed_password.decode('utf-8'),
            name=name,
            status='active',
            created=datetime.now(tz=timezone.utc),
            last_active=None
            )
        uow.users.add(user)

# TODO: Authentication enpoint has login, necessary?
# def login_exisiting_user(userID, request):
#     try:
#         curr = get_db()
#         data = request.get_json()

#         if data['type'] == 'user':
#             curr.execute("select password from User where userID=?", (userID,))
#             db_data = curr.fetchone()
#             hashed_password = db_data[0]
#             verified = bcrypt.checkpw(data['password'].encode('utf-8'), hashed_password.encode('utf-8'))

#             if not verified:
#                 raise Exception("Invalid Password")

#             curr.execute("""Update User set password=?
#                         Where userID=?""",(data['passwordNew'], userID))
#             curr.connection.commit()

#         else:
#             cred = data['credential']['credential']

#             id_info = id_token.verify_oauth2_token(cred, request, current_app.config['GOOGLE_CLIENT_ID'])
#             if id_info['aud'] != current_app.config['GOOGLE_CLIENT_ID']:
#                 raise ValueError('Could not verify audience.')

#             curr.execute("select userID,email from User where googleID=?", (id_info['sub'],))
#             data = curr.fetchone()

#             #Update Existing
#             if not data:
#                 curr.execute("""Update User set googleEmail=?, name=?, googleID=?, googleImage=?
#                             Where userID = ?
#                             """, (userID,id_info['email'], id_info['name'], id_info['sub'], id_info['picture']))
#                 curr.connection.commit()
#             elif (data[0] and not data[1]) and (data[0] != userID):
#                 #Logged into a user and has signed up seperatley with google account
#                 raise Exception("Account already exists under Google ID. Please remove this account if you wish to connect with Google.")
#         return None
#     except Exception as e:
#         return  e
#     finally:
#         curr.connection.close()

#TODO
# def delete_user_account(userID):
#     try:
#         curr = get_db()
#         curr.execute("""Update User set status='inactive' where userID=?""", (userID,))
#         curr.connection.commit()
#         curr.connection.close()
#     except Exception as e:
#         return e

#TODO
# def reset_user_account(userID):
#     try:
#         curr = get_db()
#         curr.execute("PRAGMA foreign_keys = ON")
#         curr.execute("Delete from Upload where userID = ?", (userID,))
#         curr.execute("Delete from Category where userID=?", (userID,))
#         curr.connection.commit()
#     except Exception as e:
#         return e
#     finally:
#         curr.connection.close()