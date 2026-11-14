"""Job search logic with a fake Exa client (no network)."""

from types import SimpleNamespace

import pytest

from app import exa_client, jobs


def _result(url: str) -> SimpleNamespace:
    return SimpleNamespace(url=url, title=f"Title {url}", highlights=["Duties text"])


def _deep_response(items: list[dict], result_urls: list[str]) -> SimpleNamespace:
    return SimpleNamespace(
        results=[_result(url) for url in result_urls],
        output=SimpleNamespace(content={"jobs": items}),
    )


@pytest.fixture
def live(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EXA_API_KEY", "test")


def test_build_query_keeps_user_words() -> None:
    query = jobs.build_query("Tampere", "hyvä Excelissä, ei myyntiä", "liian kaukana")
    assert "hyvä Excelissä, ei myyntiä" in query
    assert "Tampere" in query
    assert "liian kaukana" in query


def test_search_drops_invented_seen_and_duplicate_urls(
    live: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    items = [
        {"title": "A", "url": "https://a.fi/1", "summary": "s"},
        {"title": "Invented", "url": "https://fake.fi/x", "summary": "s"},
        {"title": "Seen", "url": "https://a.fi/2", "summary": "s"},
        {"title": "A again", "url": "https://a.fi/1", "summary": "s"},
        {"title": "B", "url": "https://b.fi/3", "summary": "s", "deadline": "1.12.2026"},
    ]
    response = _deep_response(items, ["https://a.fi/1", "https://a.fi/2", "https://b.fi/3"])
    monkeypatch.setattr(exa_client, "deep_search", lambda *args: response)

    found = jobs.search_jobs("Tampere", "toive", exclude_urls=["https://a.fi/2"])

    assert [job.url for job in found] == ["https://a.fi/1", "https://b.fi/3"]
    assert found[1].deadline == "1.12.2026"


def test_search_handles_json_string_output(live: None, monkeypatch: pytest.MonkeyPatch) -> None:
    response = _deep_response([], ["https://a.fi/1"])
    response.output.content = '{"jobs": [{"title": "A", "url": "https://a.fi/1"}]}'
    monkeypatch.setattr(exa_client, "deep_search", lambda *args: response)

    assert [job.title for job in jobs.search_jobs("", "toive", [])] == ["A"]


def test_similar_keeps_wish_and_skips_liked(live: None, monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[str] = []

    def fake_search(query: str, *args: object) -> SimpleNamespace:
        calls.append(query)
        return _deep_response([], ["https://a.fi/1", "https://b.fi/2"])

    monkeypatch.setattr(exa_client, "deep_search", fake_search)
    liked = jobs.Job(title="Hankinta-assistentti", url="https://a.fi/1", summary="Kilpailutus")

    found = jobs.similar_jobs("Tampere", "ei myyntiä", liked, exclude_urls=[])

    assert [job.url for job in found] == ["https://b.fi/2"]
    assert "ei myyntiä" in calls[0] and "Hankinta-assistentti" in calls[0]


def test_search_tops_up_from_plain_results(live: None, monkeypatch: pytest.MonkeyPatch) -> None:
    urls = ["https://a.fi/1", "https://linkedin.com/in/someone", "https://b.fi/2", "https://c.fi/3"]
    response = _deep_response([{"title": "A", "url": "https://a.fi/1"}], urls)
    monkeypatch.setattr(exa_client, "deep_search", lambda *args: response)

    found = jobs.search_jobs("", "toive", exclude_urls=["https://c.fi/3"])

    assert [job.url for job in found] == ["https://a.fi/1", "https://b.fi/2"]


def test_repeat_search_uses_cache(live: None, monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[str] = []

    def fake_search(query: str, *args: object) -> SimpleNamespace:
        calls.append(query)
        return _deep_response([{"title": "A", "url": "https://a.fi/1"}], ["https://a.fi/1"])

    monkeypatch.setattr(exa_client, "deep_search", fake_search)

    first = jobs.search_jobs("Tampere", "toive", [])
    second = jobs.search_jobs("Tampere", "toive", exclude_urls=["https://a.fi/1"])

    assert len(calls) == 1
    assert [job.url for job in first] == ["https://a.fi/1"]
    assert second == []


def test_stub_without_key() -> None:
    assert jobs.search_jobs("", "mitä tahansa", [])[0].url.startswith("https://example.com")
