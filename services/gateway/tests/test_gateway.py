from fastapi.testclient import TestClient
from gateway.main import app

client = TestClient(app)


def test_gateway_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_gateway_languages():
    response = client.get("/api/languages")
    assert response.status_code == 200
    assert "languages" in response.json()
