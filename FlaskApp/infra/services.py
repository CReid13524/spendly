import sqlite3
from functools import wraps

from flask import g, abort


# TODO: Remove get_db
def get_db():
    database = r'FlaskApp/spendly.db'
    db = sqlite3.connect(database)
    return db.cursor()


def require_auth(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if g.current_user is None:
            abort(401, description="Authentication required")
        return fn(*args, **kwargs)

    return wrapper
