from flask import Flask
from flask_restx import Api
from flask_cors import CORS
import os
from dotenv import load_dotenv
from FlaskApp.serv.services import get_db


def create_app():
    app = Flask(__name__)
    api = Api(app)
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

    load_dotenv(r"FlaskApp/.env")
    app.config['SECURE_KEY'] = os.getenv('SECURE_KEY')
    app.config['GOOGLE_CLIENT_ID'] = os.getenv('GOOGLE_CLIENT_ID')
    app.config['FLASK_ENVIRONMENT'] = os.getenv('FLASK_ENVIRONMENT','local')
    with open(r"FlaskApp/spendly.sql") as sql_file:
        s = sql_file.read()
    curr = get_db()
    curr.executescript(s)
    curr.connection.commit()
    curr.connection.close()

    # Blueprints
    from FlaskApp.serv.user import User
    api.add_resource(User, '/user')
    from FlaskApp.serv.authentication import Authentication
    api.add_resource(Authentication, '/authentication', '/authentication/<string:email>')
    from FlaskApp.serv.transactions import Transaction
    api.add_resource(Transaction, '/transactions', '/transactions/<int:count>/<string:categoryID>', '/transactions/<int:count>','/transactions_filter/<int:count>/<string:date>','/transactions_mass_delete')
    from FlaskApp.serv.categories import Category
    api.add_resource(Category, '/categories','/categories/<string:advanced>','/categories/<string:advanced>/<string:date>')
    from FlaskApp.serv.map import Map
    api.add_resource(Map, '/map')
    from FlaskApp.serv.search import Search
    api.add_resource(Search, '/search')


    return app, api
