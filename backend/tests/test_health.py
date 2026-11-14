"""API smoke tests using the deterministic stub response."""

from fastapi.testclient import TestClient

from app.main import app
from app.schemas import Job

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
        "title", "employer", "location", "url", "deadline", "summary", "why", "status"
    }
    assert all(job["status"] in {"open", "unknown"} for job in jobs)


def test_search_response_has_status_for_every_job(monkeypatch) -> None:
    from app import main

    monkeypatch.setattr(
        main,
        "search_jobs",
        lambda *args: [
            Job(title="A", url="https://a.fi/1", summary="", status="open"),
            Job(title="B", url="https://b.fi/2", summary="", status="unknown"),
        ],
    )

    response = client.post("/jobs/search", json={"wish": "toimistotyö"})

    assert response.status_code == 200
    jobs = response.json()["jobs"]
    assert [job["status"] for job in jobs] == ["open", "unknown"]


def test_search_requires_wish() -> None:
    assert client.post("/jobs/search", json={"area": "Tampere", "wish": ""}).status_code == 422

