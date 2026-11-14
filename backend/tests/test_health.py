"""API smoke tests using the deterministic stub response."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_search_returns_response_schema() -> None:
    response = client.post("/jobs/search", json={"area": "Tampere", "wish": "toimistotyö"})
    assert response.status_code == 200
    jobs = response.json()["jobs"]
    assert jobs
    assert set(jobs[0]) == {
        "title", "employer", "location", "url", "deadline", "summary", "why"
    }


def test_search_requires_wish() -> None:
    assert client.post("/jobs/search", json={"area": "Tampere", "wish": ""}).status_code == 422

