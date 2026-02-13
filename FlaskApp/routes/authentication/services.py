import datetime
import uuid
import jwt
from flask import make_response, Request
from google.auth.transport import requests
from flask import current_app
from google.oauth2 import id_token
from FlaskApp.infra.unit_of_work import AbstractUnitOfWork
from FlaskApp.domainmodel import User, ExternalIdentity
from FlaskApp.infra.exceptions import ValidationError

def create_auth_token(user_id: uuid.UUID):
    payload = {
            'user_id':str(user_id),
            'exp': (datetime.datetime.now() + datetime.timedelta(hours=1)).timestamp()
        }
    token = jwt.encode(payload, current_app.config['SECURE_KEY'], algorithm='HS256')
    response = make_response({'success': True}, 200)
    response.set_cookie(
        'auth_token',
        token,
        max_age=3600,
        httponly=True,
        secure=current_app.config['FLASK_ENVIRONMENT'] != 'local',
        samesite='Lax' if current_app.config['FLASK_ENVIRONMENT'] == 'local' else "None"
    )
    return response

# TODO: Refactor to use uow and repositories
# def check_user_exists(email):
#     try:
#         curr = get_db()
#         curr.execute("select userID from User where email=? and status='active'", (email,))
#         res = curr.fetchone()
#         return None, res
#     except Exception as e:
#         return e, None

def login_with_google(uow: AbstractUnitOfWork, credential: str, request: Request):
    # Google login conincides with User Resource as Secure resource handles login/create for google
    with uow:

        #Veify token:
        id_info = id_token.verify_oauth2_token(credential, requests.Request(), current_app.config['GOOGLE_CLIENT_ID'])
        if id_info['aud'] != current_app.config['GOOGLE_CLIENT_ID']:
            raise ValidationError('Could not verify audience.')

        # Check if user exists, if not create new user and external identity
        is_exists = uow.users.external_id_exists('google', id_info['sub'])
        if not is_exists:
            # Create new user and identity
            user_id = uuid.uuid4()
            external_identity = ExternalIdentity(
                provider='google',
                external_id=id_info['sub'],
                email=id_info['email'],
                avatar_url=id_info['picture'],
                name=id_info['name'],
                connected_at=datetime.datetime.now()
            )
            user = User(
                user_id=user_id,
                email=id_info['email'],
                name=id_info['name'],
                password=None,
                status='active',
                created=datetime.datetime.now(),
                last_active=datetime.datetime.now() # Since google login returns auth_token, we consider the user active
                )
            uow.users.add(user)
            uow.users.add_external_identity(external_identity, user_id)
        else:
            # Just get the user
            user = uow.users.get_user_by_external_id('google', id_info['sub'])
            user_id = user.user_id

        return create_auth_token(user_id)


def login_with_details(uow: AbstractUnitOfWork, email: str, password: str):
    with uow:
        user = uow.users.get_by_email(email=email)
        # Don't want to give away which one is wrong
        if not user:
            # User doesnt exist
            raise ValidationError("Invalid email or password")
        if not user.check_password(password):
            # Password is wrong
            raise ValidationError("Invalid email or password")
        uow.users.active(user)
        return create_auth_token(user.id)
