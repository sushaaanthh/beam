from fastapi.testclient import TestClient
from app.core.config import settings
from app.api.deps import get_database_session
from app.main import app


class FakeSession:
    def execute(self, query):
        return None


client = TestClient(app)


def test_root_endpoint() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "project": settings.PROJECT_NAME,
        "version": settings.PROJECT_VERSION,
        "status": "running",
    }


def test_health_endpoint() -> None:
    app.dependency_overrides[get_database_session] = lambda: FakeSession()
    try:
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        assert response.json() == {
            "status": "healthy",
            "database": "connected",
        }
    finally:
        app.dependency_overrides.pop(get_database_session, None)
