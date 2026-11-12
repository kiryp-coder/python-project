import os

from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./shop.db")


class Base(DeclarativeBase):
    pass


def make_engine(url):
    if url.startswith("sqlite"):
        engine = create_engine(url, connect_args={"check_same_thread": False})

        @event.listens_for(engine, "connect")
        def use_python_lower(dbapi_connection, connection_record):
            dbapi_connection.create_function("lower", 1, lambda value: value.lower() if value else value)

        return engine

    return create_engine(url)


engine = make_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


def get_session():
    with SessionLocal() as session:
        yield session
