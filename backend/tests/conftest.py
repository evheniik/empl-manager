import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

import app.models  # noqa: F401 — register models on Base.metadata
from app.core.config import settings
from app.core.security import hash_password
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.user import User


def _test_database_url() -> str:
    base, _, _ = settings.DATABASE_URL.rpartition("/")
    return f"{base}/empl_manager_test"


TEST_DATABASE_URL = _test_database_url()

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def _ensure_test_database_exists() -> None:
    base, _, dbname = TEST_DATABASE_URL.rpartition("/")
    maint_engine = create_engine(f"{base}/postgres", isolation_level="AUTOCOMMIT")
    with maint_engine.connect() as conn:
        exists = conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :name"),
            {"name": dbname},
        ).first()
        if exists is None:
            conn.execute(text(f'CREATE DATABASE "{dbname}"'))
    maint_engine.dispose()


@pytest.fixture(scope="session")
def _schema():
    _ensure_test_database_exists()
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db(_schema):
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        with TestingSessionLocal() as cleanup:
            for table in reversed(Base.metadata.sorted_tables):
                cleanup.execute(table.delete())
            cleanup.commit()


@pytest.fixture()
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def user_credentials(db):
    email = f"user-{uuid.uuid4().hex[:12]}@example.com"
    password = "secret123"
    user = User(email=email, hashed_password=hash_password(password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"email": email, "password": password}


@pytest.fixture()
def auth_headers(client, user_credentials):
    resp = client.post(
        "/api/v1/auth/login",
        data={
            "username": user_credentials["email"],
            "password": user_credentials["password"],
        },
    )
    assert resp.status_code == 200, resp.text
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}
