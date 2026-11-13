"""API smoke tests using the deterministic scaffold response."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_claim_returns_response_schema() -> None:
    response = client.post("/claim", json={"description": "My flight was delayed."})
    assert response.status_code == 200
    payload = response.json()
    assert set(payload) == {"answer", "sources", "draft_letter"}
    assert payload["answer"]
    assert payload["draft_letter"]
    assert payload["sources"]
    assert set(payload["sources"][0]) == {"title", "url", "quote"}
