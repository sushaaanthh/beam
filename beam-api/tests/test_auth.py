from __future__ import annotations

from collections.abc import Generator
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.api.deps import get_database_session
from app.database.base import Base
from app.main import app
from app.models.user import User

TEST_DB_PATH = Path(__file__).with_name("test_auth.sqlite")
TEST_DATABASE_URL = f"sqlite:///{TEST_DB_PATH}"

if TEST_DB_PATH.exists():
    TEST_DB_PATH.unlink()

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base.metadata.create_all(bind=engine, tables=[User.__table__])


def override_get_database_session() -> Generator[Session, None, None]:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_database_session] = override_get_database_session
client = TestClient(app)


def test_auth_flow() -> None:
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "jane_doe",
            "email": "jane@example.com",
            "password": "StrongPass123",
        },
    )
    assert register_response.status_code == 201
    assert register_response.json() == {"message": "User created successfully"}

    login_response = client.post(
        "/api/v1/auth/login",
        data={"username": "jane_doe", "password": "StrongPass123"},
    )
    assert login_response.status_code == 200
    tokens = login_response.json()
    assert tokens["access_token"]
    assert tokens["refresh_token"]
    assert tokens["token_type"] == "bearer"

    me_response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    assert me_response.status_code == 200
    assert me_response.json()["username"] == "jane_doe"
    assert me_response.json()["email"] == "jane@example.com"

    refresh_response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]},
    )
    assert refresh_response.status_code == 200
    refreshed_tokens = refresh_response.json()
    assert refreshed_tokens["access_token"]

    logout_response = client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
        json={"refresh_token": refreshed_tokens["refresh_token"]},
    )
    assert logout_response.status_code == 200
    assert logout_response.json() == {"message": "Logged out successfully"}
