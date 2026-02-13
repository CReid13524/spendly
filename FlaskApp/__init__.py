import os

import jwt
from dotenv import load_dotenv
from flask import Flask, request, g
from flask_cors import CORS
from flask_restx import Api

from FlaskApp.infra.unit_of_work import SqlAlchemyUnitOfWork, AbstractUnitOfWork


def create_app():
    app = Flask(__name__)
    api = Api(app, title='Spendly API', description='API for Spendly application')
    CORS(
        app,
        resources={
            r"/*": {
                "origins": [
                    "http://127.0.0.1:8000",
                    "https://spendly-dev.azurewebsites.net",
                    "http://spendly-dev.azurewebsites.net"
                ]
            }
        },
        supports_credentials=True
    )

    # Load app config
    load_dotenv(r"FlaskApp/.env")
    app.config['SECURE_KEY'] = os.getenv('SECURE_KEY')
    app.config['GOOGLE_CLIENT_ID'] = os.getenv('GOOGLE_CLIENT_ID')
    app.config['FLASK_ENVIRONMENT'] = os.getenv('FLASK_ENVIRONMENT', 'local')
    app.config['DATABASE_URL'] = os.getenv('DATABASE_URL')

    # Initialise database
    from FlaskApp.infra.db import init_db
    with app.app_context():
        _, SessionLocal = init_db(app.config['DATABASE_URL'])

    # Load user before each request
    @app.before_request
    def load_current_user():
        g.current_user = None

        token = request.cookies.get("auth_token")
        if not token:
            return
        uow: AbstractUnitOfWork = SqlAlchemyUnitOfWork(SessionLocal)

        with uow:
            try:
                payload = jwt.decode(token, app.config['SECURE_KEY'], algorithms=["HS256"])
                user = uow.users.get(payload["user_id"])
                g.current_user = user
                uow.users.active(user)
            except jwt.InvalidTokenError:
                # Invalid token, ignore and treat as unauthenticated
                pass

    # Blueprints / Namespaces
    from FlaskApp.routes.akahu import ns as akahu_ns
    api.add_namespace(akahu_ns, path='/akahu')
    from FlaskApp.routes.authentication import ns as auth_ns
    api.add_namespace(auth_ns, path='/authenticate')
    from FlaskApp.routes.user import ns as user_ns
    api.add_namespace(user_ns, path='/user')
    # TODO: Add disconnected blueprints here as needed

    return app, api
