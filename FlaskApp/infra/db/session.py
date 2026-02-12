from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def init_session(database_url: str):
    engine = create_engine(database_url)
    SessionLocal = sessionmaker(bind=engine)

    return engine, SessionLocal
