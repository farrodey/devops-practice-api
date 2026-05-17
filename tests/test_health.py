from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_liveness_endpoint_returns_alive() -> None:
    response = client.get("/health/live")

    assert response.status_code == 200
    assert response.json()["status"] == "alive"


def test_root_endpoint_contains_docs_and_health_links() -> None:
    response = client.get("/")

    assert response.status_code == 200

    payload = response.json()
    assert payload["docs"] == "/docs"
    assert payload["health"]["live"] == "/health/live"
    assert payload["health"]["ready"] == "/health/ready"
