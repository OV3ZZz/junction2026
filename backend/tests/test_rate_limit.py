"""The global search limit protects API credits in the demo."""

import pytest
from fastapi.testclient import TestClient

from app import rate_limit
from app.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def fresh_limit() -> None:
    rate_limit.reset()


def test_search_is_rejected_after_hourly_limit(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MAX_SEARCHES_PER_HOUR", "2")
    body = {"wish": "toimistotyö"}

    assert client.post("/jobs/search", json=body).status_code == 200
    assert client.post("/jobs/search", json=body).status_code == 200
    assert client.post("/jobs/search", json=body).status_code == 429


def test_zero_disables_limit(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MAX_SEARCHES_PER_HOUR", "0")
    for _ in range(3):
        assert client.post("/jobs/search", json={"wish": "kesätyö"}).status_code == 200
