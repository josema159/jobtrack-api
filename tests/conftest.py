import os

import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool


# Configuración exclusiva para tests.
# Debe establecerse antes de importar la aplicación.
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"


from app import models
from app.database import Base, get_db
from app.main import app


TEST_DATABASE_URL = "sqlite://"


test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={
        "check_same_thread": False
    },
    poolclass=StaticPool
)


TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    autocommit=False
)


def override_get_db():
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def reset_database():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    yield


@pytest.fixture
def client():
    return TestClient(app)