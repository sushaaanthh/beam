from __future__ import annotations

import uuid
from collections.abc import Generator
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.api.deps import get_database_session
from app.database.base import Base
from app.main import app
from app.models.analysis_session import AnalysisSession

TEST_DB_PATH = Path(__file__).with_name("test_analysis.sqlite")
TEST_DATABASE_URL = f"sqlite:///{TEST_DB_PATH}"

if TEST_DB_PATH.exists():
    TEST_DB_PATH.unlink()

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base.metadata.create_all(bind=engine)

SAMPLE_TEXT = (
    "The release went smoothly and the whole team was thrilled "
    "with how the community responded to the announcement."
)


@pytest.fixture()
def db_session_override() -> Generator[None, None, None]:
    """Override the DB dependency per-test and restore whatever was there before.

    Other test modules in this project patch the same dependency at module
    import time; restoring state keeps `pytest tests` runs stable.
    """
    previous = app.dependency_overrides.get(get_database_session)

    def override() -> Generator[Session, None, None]:
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_database_session] = override
    yield
    if previous is not None:
        app.dependency_overrides[get_database_session] = previous
    else:
        app.dependency_overrides.pop(get_database_session, None)


@pytest.fixture()
def client(db_session_override: None) -> Generator[TestClient, None, None]:
    with TestClient(app) as test_client:
        yield test_client


def _register_and_login(client: TestClient, suffix: str) -> dict[str, str]:
    register = client.post(
        "/api/v1/auth/register",
        json={
            "username": f"analyst_{suffix}",
            "email": f"analyst_{suffix}@example.com",
            "password": "StrongPass123",
        },
    )
    assert register.status_code == 201, register.text

    login = client.post(
        "/api/v1/auth/login",
        data={"username": f"analyst_{suffix}", "password": "StrongPass123"},
    )
    assert login.status_code == 200, login.text
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# --------------------------------------------------------------------------
# Authentication
# --------------------------------------------------------------------------

def test_create_requires_authentication(client: TestClient) -> None:
    response = client.post(
        "/api/v1/analysis",
        json={"text": SAMPLE_TEXT, "source_type": "text"},
    )
    assert response.status_code == 401


def test_list_requires_authentication(client: TestClient) -> None:
    assert client.get("/api/v1/analysis").status_code == 401


def test_detail_requires_authentication(client: TestClient) -> None:
    assert client.get(f"/api/v1/analysis/{uuid.uuid4()}").status_code == 401


def test_delete_requires_authentication(client: TestClient) -> None:
    assert client.delete(f"/api/v1/analysis/{uuid.uuid4()}").status_code == 401


# --------------------------------------------------------------------------
# Creation + validation
# --------------------------------------------------------------------------

def test_create_analysis_completes_without_fabricated_predictions(client: TestClient) -> None:
    headers = _register_and_login(client, "create")

    created = client.post(
        "/api/v1/analysis",
        json={"text": SAMPLE_TEXT, "source_type": "text"},
        headers=headers,
    )
    assert created.status_code == 201, created.text
    body = created.json()
    assert body["status"] == "completed"
    session_id = body["session_id"]
    uuid.UUID(str(session_id))

    detail = client.get(f"/api/v1/analysis/{session_id}", headers=headers)
    assert detail.status_code == 200
    payload = detail.json()

    # Status transitioned through the placeholder service.
    assert payload["status"] == "completed"
    assert payload["completed_at"] is not None

    # Input metadata is real.
    assert payload["input"]["raw_text"] == SAMPLE_TEXT
    assert payload["input"]["char_count"] == len(SAMPLE_TEXT)
    assert payload["input"]["word_count"] == len(SAMPLE_TEXT.split())

    # Model-dependent outputs are explicitly absent, never fabricated.
    assert payload["prediction"] is None
    assert payload["primary_emotion"] is None
    assert payload["confidence"] is None
    assert payload["behavior_metrics"] is None
    assert payload["explanation"] is None
    assert payload["model_info"]["deployed"] is False
    assert "not deployed" in (payload["model_info"]["note"] or "")


def test_create_rejects_empty_text(client: TestClient) -> None:
    headers = _register_and_login(client, "empty")
    for text in ("", "   \n\t  "):
        response = client.post(
            "/api/v1/analysis",
            json={"text": text, "source_type": "text"},
            headers=headers,
        )
        assert response.status_code == 422, f"text={text!r} -> {response.status_code}"


def test_create_rejects_oversized_text_with_413(client: TestClient) -> None:
    headers = _register_and_login(client, "oversize")
    from app.core.config import settings

    oversized = "a" * (settings.MAX_ANALYSIS_TEXT_CHARS + 1)
    response = client.post(
        "/api/v1/analysis",
        json={"text": oversized, "source_type": "text"},
        headers=headers,
    )
    assert response.status_code == 413
    assert "maximum" in response.json()["detail"].lower()


def test_create_rejects_missing_fields(client: TestClient) -> None:
    headers = _register_and_login(client, "missing")
    response = client.post("/api/v1/analysis", json={}, headers=headers)
    assert response.status_code == 422


# --------------------------------------------------------------------------
# Ownership / privacy
# --------------------------------------------------------------------------

def test_user_cannot_access_another_users_session(client: TestClient) -> None:
    owner_headers = _register_and_login(client, "owner")
    intruder_headers = _register_and_login(client, "intruder")

    created = client.post(
        "/api/v1/analysis",
        json={"text": SAMPLE_TEXT, "source_type": "text"},
        headers=owner_headers,
    )
    session_id = created.json()["session_id"]

    assert client.get(
        f"/api/v1/analysis/{session_id}", headers=intruder_headers
    ).status_code == 404
    assert client.delete(
        f"/api/v1/analysis/{session_id}", headers=intruder_headers
    ).status_code == 404

    list_response = client.get("/api/v1/analysis", headers=intruder_headers)
    ids = [item["session_id"] for item in list_response.json()["items"]]
    assert str(session_id) not in ids


# --------------------------------------------------------------------------
# Retrieval: list, search, filter, sort, pagination
# --------------------------------------------------------------------------

def _create_sessions(client: TestClient, headers: dict[str, str], titles: list[str]) -> list[str]:
    ids = []
    for title in titles:
        response = client.post(
            "/api/v1/analysis",
            json={"text": f"sample corpus text {title}", "source_type": "text", "title": title},
            headers=headers,
        )
        assert response.status_code == 201
        ids.append(response.json()["session_id"])
    return ids


def _set_created_at(session_id: str, created_at: datetime) -> None:
    """SQLite CURRENT_TIMESTAMP has second resolution; pin explicit timestamps
    so date-sorting assertions are deterministic."""
    with TestingSessionLocal() as db:
        record = db.get(AnalysisSession, uuid.UUID(session_id))
        assert record is not None
        record.created_at = created_at
        db.commit()


def test_list_supports_pagination_search_filter_sort(client: TestClient) -> None:
    headers = _register_and_login(client, "list")
    alpha_id, beta_id, gamma_id = _create_sessions(
        client, headers, ["alpha report", "beta report", "gamma memo"]
    )

    base_time = datetime(2026, 8, 23, 12, 0, 0, tzinfo=timezone.utc)
    _set_created_at(alpha_id, base_time)
    _set_created_at(beta_id, base_time + timedelta(minutes=1))
    _set_created_at(gamma_id, base_time + timedelta(minutes=2))

    default_list = client.get("/api/v1/analysis", headers=headers).json()
    assert default_list["total"] == 3
    assert default_list["page_size"] == 20
    assert len(default_list["items"]) == 3

    # Sort ascending puts the oldest first ("alpha" was created first).
    asc = client.get("/api/v1/analysis?sort=created_asc", headers=headers).json()
    assert [item["title"] for item in asc["items"]] == [
        "alpha report",
        "beta report",
        "gamma memo",
    ]

    desc = client.get("/api/v1/analysis?sort=created_desc", headers=headers).json()
    assert desc["items"][0]["title"] == "gamma memo"

    search = client.get("/api/v1/analysis?search=beta", headers=headers).json()
    assert search["total"] == 1
    assert search["items"][0]["title"] == "beta report"

    body_search = client.get("/api/v1/analysis?search=memo corpus", headers=headers).json()
    assert body_search["total"] == 0  # search matches exact substrings only
    content_search = client.get("/api/v1/analysis?search=text gamma", headers=headers).json()
    assert content_search["total"] == 1
    assert content_search["items"][0]["title"] == "gamma memo"

    paginated = client.get(
        "/api/v1/analysis?page=2&page_size=2&sort=created_asc", headers=headers
    ).json()
    assert paginated["page"] == 2
    assert paginated["pages"] == 2
    assert len(paginated["items"]) == 1
    assert paginated["items"][0]["title"] == "gamma memo"

    invalid_status = client.get("/api/v1/analysis?status=bogus", headers=headers)
    assert invalid_status.status_code == 422

    completed = client.get("/api/v1/analysis?status=completed", headers=headers).json()
    assert completed["total"] == 3
    failed = client.get("/api/v1/analysis?status=failed", headers=headers).json()
    assert failed["total"] == 0


# --------------------------------------------------------------------------
# Deletion + cascade
# --------------------------------------------------------------------------

def test_delete_removes_session_and_children(client: TestClient) -> None:
    headers = _register_and_login(client, "deleter")
    session_id = _create_sessions(client, headers, ["to be deleted"])[0]

    deleted = client.delete(f"/api/v1/analysis/{session_id}", headers=headers)
    assert deleted.status_code == 200
    assert deleted.json() == {"message": "Analysis deleted successfully"}

    assert client.get(f"/api/v1/analysis/{session_id}", headers=headers).status_code == 404
    listing = client.get("/api/v1/analysis", headers=headers).json()
    assert listing["total"] == 0

    # Deleting again is a clean 404.
    assert client.delete(f"/api/v1/analysis/{session_id}", headers=headers).status_code == 404


def test_delete_unknown_session_returns_404(client: TestClient) -> None:
    headers = _register_and_login(client, "unknown")
    response = client.delete(f"/api/v1/analysis/{uuid.uuid4()}", headers=headers)
    assert response.status_code == 404
