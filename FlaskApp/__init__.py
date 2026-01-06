from flask import Flask
from flask_restx import Api
import os
from dotenv import load_dotenv
from FlaskApp.services import get_db


def create_app():
    app = Flask(__name__)
    api = Api(app)
    load_dotenv(r".env")
    app.config['SECURE_KEY'] = os.getenv('SECURE_KEY')
    app.config['GOOGLE_CLIENT_ID'] = os.getenv('GOOGLE_CLIENT_ID')
    with open(r"spendly.sql") as sql_file:
        s = sql_file.read()
    curr = get_db()
    curr.executescript(s)
    curr.connection.commit()
    curr.connection.close()

    # Blueprints
    from .user import User
    api.add_resource(User, '/user')
    from .authentication import Authentication
    api.add_resource(Authentication, '/authentication', '/authentication/<string:email>')
    from .transactions import Transaction
    api.add_resource(Transaction, '/transactions', '/transactions/<int:count>/<string:categoryID>', '/transactions/<int:count>','/transactions_filter/<int:count>/<string:date>','/transactions_mass_delete')
    from .categories import Category
    api.add_resource(Category, '/categories','/categories/<string:advanced>','/categories/<string:advanced>/<string:date>')
    from .map import Map
    api.add_resource(Map, '/map')
    from .search import Search
    api.add_resource(Search, '/search')


    return app, api
