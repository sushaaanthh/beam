from fastapi.testclient import TestClient

from app.api.deps import get_database_session
from app.main import app


class FakeSession:
    def execute(self, query):
        return None


app.dependency_overrides[get_database_session] = lambda: FakeSession()

client = TestClient(app)


def test_root_endpoint() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "project": "B.E.A.M.",
        "version": "1.0.0",
        "status": "running",
    }


def test_health_endpoint() -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "database": "connected",
    }
