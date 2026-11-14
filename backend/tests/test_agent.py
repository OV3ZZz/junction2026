"""Agent loop tests with a fake Gemini and fake Exa."""

from types import SimpleNamespace
from typing import Any

import pytest

from app import agent
from app.schemas import Source


class FakeMessage:
    """Minimal stand-in for an OpenAI-compatible assistant message."""

    def __init__(self, content: str | None = None, tool_calls: list[Any] | None = None) -> None:
        self.content = content
        self.tool_calls = tool_calls

    def model_dump(self, exclude_none: bool = False) -> dict[str, Any]:
        return {"role": "assistant", "content": self.content}


def _search_call(query: str) -> SimpleNamespace:
    function = SimpleNamespace(name="search_web", arguments=f'{{"query": "{query}"}}')
    return SimpleNamespace(id=f"call-{query}", function=function)


def _fake_search(query: str, include_domains: list[str] | None = None) -> list[Source]:
    return [Source(title=f"Result for {query}", url=f"https://example.org/{query}", quote="q")]


@pytest.fixture
def live(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setattr(agent, "search_web", _fake_search)
    monkeypatch.setattr(agent, "build_draft", lambda *args: "Hei, kirje")


def test_loop_searches_then_answers(live: None, monkeypatch: pytest.MonkeyPatch) -> None:
    replies = iter([
        FakeMessage(tool_calls=[_search_call("a")]),
        FakeMessage(tool_calls=[_search_call("b")]),
        FakeMessage(content="Sinulla on oikeus korvaukseen [S2]."),
    ])
    monkeypatch.setattr(agent, "chat", lambda *args, **kwargs: next(replies))

    response = agent.handle_claim("Lento myöhästyi")

    assert response.answer == "Sinulla on oikeus korvaukseen [S2]."
    assert [source.url for source in response.sources] == ["https://example.org/b"]
    assert response.draft_letter == "Hei, kirje"


def test_loop_stops_after_max_rounds(live: None, monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[dict[str, Any]] = []

    def fake_chat(messages: list[dict[str, Any]], **kwargs: Any) -> FakeMessage:
        calls.append(kwargs)
        if kwargs.get("tool_choice") == "none":
            return FakeMessage(content="Lopullinen vastaus")
        return FakeMessage(tool_calls=[_search_call(str(len(calls)))])

    monkeypatch.setattr(agent, "chat", fake_chat)

    response = agent.handle_claim("Lento myöhästyi")

    assert len(calls) == agent.MAX_ROUNDS + 1
    assert response.answer == "Lopullinen vastaus"
    assert len(response.sources) == agent.MAX_ROUNDS
