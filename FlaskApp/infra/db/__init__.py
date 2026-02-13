import FlaskApp.infra.db.orm
from FlaskApp.infra.db.base import Base
from FlaskApp.infra.db.session import init_session

engine, SessionLocal = None, None


def init_db(database_url: str):
    global engine, SessionLocal
    engine, SessionLocal = init_session(database_url)
    Base.metadata.create_all(bind=engine)
    return engine, SessionLocal
