"""Exa adapter options without making network requests."""

from types import SimpleNamespace

from app import exa_client


def test_deep_search_excludes_stale_job_aggregators(monkeypatch) -> None:
    captured: dict[str, object] = {}

    def fake_search(query: str, **kwargs: object) -> object:
        captured.update(kwargs)
        return SimpleNamespace(results=[], output=None)

    monkeypatch.setattr(exa_client, "_client", lambda: SimpleNamespace(search=fake_search))

    exa_client.deep_search("query", "prompt", {"type": "object"})

    assert captured["exclude_domains"] == [
        "bebee.com", "jooble.org", "careerjet.fi", "jobleads.com", "drjobpro.com"
    ]
