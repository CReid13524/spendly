from http import HTTPStatus
import sqlite3
from functools import wraps

from flask import g, abort, make_response
from flask_restx import Namespace
from FlaskApp.infra.models import register_global_models_to_namespace
from FlaskApp.infra.exceptions import Unauthorized

app_ns = Namespace('__App__', description='Internal namespace for application-wide models and services')
models = register_global_models_to_namespace(app_ns)


# TODO: Remove get_db
def get_db():
    database = r'FlaskApp/spendly.db'
    db = sqlite3.connect(database)
    return db.cursor()


def require_auth(fn=None, ns=None):
    """Decorator for authentication, supports both @require_auth and @require_auth(ns=ns)."""
    def decorator(inner_fn):
        @wraps(inner_fn)
        def wrapper(*args, **kwargs):
            if g.current_user is None:
                from flask import jsonify
                raise Unauthorized()
            return inner_fn(*args, **kwargs)
        # Attach Swagger response if namespace provided
        if ns is not None:
            wrapper = ns.response(HTTPStatus.UNAUTHORIZED, 'Unauthorized', model=models['RequireAuth'])(wrapper)
        return wrapper
    # Support both @require_auth and @require_auth(ns=ns)
    if fn is not None:
        return decorator(fn)
    return decorator
