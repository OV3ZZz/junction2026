"""Job search logic with a fake Exa client (no network)."""

from types import SimpleNamespace

import pytest

from app import exa_client, jobs
from app.schemas import SeenJob


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


def test_prompt_uses_free_form_location_without_finland_only_restriction() -> None:
    prompt = jobs.system_prompt()

    assert "Respect the location in the query" in prompt
    assert "without a geographic restriction" in prompt
    assert "interpret it as the Finnish location" in prompt
    assert "in Finland" not in prompt


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


def test_search_shows_only_structured_jobs(live: None, monkeypatch: pytest.MonkeyPatch) -> None:
    # Raw results without a summary are not turned into cards any more.
    urls = ["https://a.fi/1", "https://b.fi/2"]
    response = _deep_response([{"title": "A", "url": "https://a.fi/1", "summary": "s"}], urls)
    monkeypatch.setattr(exa_client, "deep_search", lambda *args: response)

    assert [job.url for job in jobs.search_jobs("", "toive", [])] == ["https://a.fi/1"]


def test_search_drops_expired_and_formats_deadline(
    live: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    items = [
        {"title": "Old", "url": "https://a.fi/1", "deadline": "2000-08-02"},
        {"title": "Open", "url": "https://b.fi/2", "deadline": "2999-11-19"},
    ]
    response = _deep_response(items, ["https://a.fi/1", "https://b.fi/2"])
    monkeypatch.setattr(exa_client, "deep_search", lambda *args: response)

    found = jobs.search_jobs("", "toive", [])

    assert [(job.title, job.deadline) for job in found] == [("Open", "19.11.2999")]


def test_search_drops_closed_keeps_unknown_and_sorts_open_first(
    live: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    items = [
        {"title": "Unknown", "url": "https://a.fi/unknown", "status": "unknown"},
        {"title": "Closed", "url": "https://a.fi/closed", "status": "closed"},
        {"title": "Open", "url": "https://a.fi/open", "status": "open"},
    ]
    urls = [item["url"] for item in items]
    monkeypatch.setattr(exa_client, "deep_search", lambda *args: _deep_response(items, urls))

    found = jobs.search_jobs("", "toive", [])

    assert [(job.title, job.status) for job in found] == [
        ("Open", "open"),
        ("Unknown", "unknown"),
    ]


def test_search_drops_unknown_with_expired_deadline(
    live: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    items = [
        {"title": "Unknown expired", "url": "https://a.fi/expired", "status": "unknown",
         "deadline": "2000-08-02"},
        {"title": "Unknown without deadline", "url": "https://a.fi/unknown", "status": "unknown"},
    ]
    urls = [item["url"] for item in items]
    monkeypatch.setattr(exa_client, "deep_search", lambda *args: _deep_response(items, urls))

    found = jobs.search_jobs("", "toive", [])

    assert [job.url for job in found] == ["https://a.fi/unknown"]


def test_unrecognized_status_is_kept_as_unknown(
    live: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    items = [{"title": "No status", "url": "https://a.fi/1"}]
    monkeypatch.setattr(exa_client, "deep_search", lambda *args: _deep_response(items, [items[0]["url"]]))

    found = jobs.search_jobs("", "toive", [])

    assert found[0].status == "unknown"


def test_search_skips_same_job_on_another_site(
    live: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    items = [
        {"title": "Hankinta-assistentti", "employer": "HankintaPartners Oy",
         "url": "https://duunitori.fi/1"},
        {"title": "Hankinta-assistentti, HankintaPartners Oy", "employer": "Eilakaisla Oy",
         "url": "https://laura.fi/2"},
        {"title": "Asiakaspalvelija", "employer": "Firma Oy", "url": "https://iisihaku.fi/3"},
        {"title": "Junior Developer", "employer": "Vuono Group", "url": "https://vuono.fi/4"},
    ]
    urls = [item["url"] for item in items]
    monkeypatch.setattr(exa_client, "deep_search", lambda *args: _deep_response(items, urls))
    already_shown = [SeenJob(title="Junior Developer | Duunitori", employer="Vuono Group Oy")]

    found = jobs.search_jobs("", "toive", [], seen_jobs=already_shown)

    assert [job.url for job in found] == ["https://duunitori.fi/1", "https://iisihaku.fi/3"]


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
