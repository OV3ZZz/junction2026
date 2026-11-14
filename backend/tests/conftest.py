"""Shared test setup: never call live APIs from tests."""

import pytest

from app import cache


@pytest.fixture(autouse=True)
def no_live_keys(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("EXA_API_KEY", raising=False)


@pytest.fixture(autouse=True)
def empty_cache() -> None:
    cache.clear()
