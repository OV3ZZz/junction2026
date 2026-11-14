"""The global /claim limit protects API credits in the public demo."""

import pytest
from fastapi.testclient import TestClient

from app import rate_limit
from app.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def fresh_limit() -> None:
    rate_limit.reset()


def test_claim_is_rejected_after_hourly_limit(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MAX_CLAIMS_PER_HOUR", "2")
    body = {"description": "Lento myöhästyi"}

    assert client.post("/claim", json=body).status_code == 200
    assert client.post("/claim", json=body).status_code == 200
    assert client.post("/claim", json=body).status_code == 429


def test_zero_disables_limit(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MAX_CLAIMS_PER_HOUR", "0")
    for _ in range(3):
        assert client.post("/claim", json={"description": "Lasku väärin"}).status_code == 200
