"""Shared test setup: never call live APIs from tests."""

import pytest


@pytest.fixture(autouse=True)
def no_live_keys(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("EXA_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
