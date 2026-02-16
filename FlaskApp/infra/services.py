from functools import wraps
from http import HTTPStatus

from flask import g
from flask_restx import Namespace

from FlaskApp.infra.exceptions import Unauthorized
from FlaskApp.infra.models import register_global_models_to_namespace

app_ns = Namespace('__App__', description='Internal namespace for application-wide models and services')
models = register_global_models_to_namespace(app_ns)

OK_RESPONSE = {"success": True}, HTTPStatus.OK
CREATED_RESPONSE = {"success": True}, HTTPStatus.CREATED


def make_ok_response(**kwargs):
    response = {"success": True}
    response.update(kwargs)
    return response, HTTPStatus.OK


def require_auth(fn=None, ns=None):
    """Decorator for authentication, supports both @require_auth and @require_auth(ns=ns)."""
    def decorator(inner_fn):
        @wraps(inner_fn)
        def wrapper(*args, **kwargs):
            if g.current_user is None:
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
