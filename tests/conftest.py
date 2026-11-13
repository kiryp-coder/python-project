import os

os.environ["CELERY_BROKER_URL"] = "memory://"
os.environ["CELERY_RESULT_BACKEND"] = "cache+memory://"
os.environ["CELERY_TASK_ALWAYS_EAGER"] = "true"
os.environ["RECEIPT_SECONDS"] = "0"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.config import ADMIN_EMAIL, ADMIN_PASSWORD
from app.database import Base, get_session, make_engine
from app.limiter import limiter
from app.main import app
from app.seed import add_admin, add_starting_products


@pytest.fixture
def client(tmp_path):
    engine = make_engine(f"sqlite:///{tmp_path / 'test.db'}")
    TestSession = sessionmaker(bind=engine, expire_on_commit=False)
    Base.metadata.create_all(engine)

    with TestSession() as session:
        add_starting_products(session)
        add_admin(session)

    def get_test_session():
        with TestSession() as session:
            yield session

    limiter.reset()
    app.dependency_overrides[get_session] = get_test_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    engine.dispose()


def register(client, email, password="secret123", name="Тестовый Пользователь"):
    return client.post("/auth/register", json={"name": name, "email": email, "password": password})


def login(client, email, password):
    return client.post("/auth/login", data={"username": email, "password": password})


def auth_header(client, email, password):
    token = login(client, email, password).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_headers(client):
    return auth_header(client, ADMIN_EMAIL, ADMIN_PASSWORD)


@pytest.fixture
def anna(client):
    user = register(client, "anna@example.com", name="Анна").json()
    user["headers"] = auth_header(client, "anna@example.com", "secret123")
    return user
