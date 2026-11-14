"""Bounded Gemini + Exa agent loop for research-backed consumer claim assistance."""

import json
import re
from typing import Any

from .config import get_gemini_key
from .draft import build_draft
from .exa_client import search_web
from .llm import chat
from .schemas import ClaimResponse, Source

MAX_ROUNDS = 5

SYSTEM_PROMPT = """You are Reklama, an assistant that helps consumers in Finland and the EU \
work out whether they may be entitled to compensation (delayed or cancelled flights, defective \
products, incorrect invoices and similar).

How to work:
- Use the search_web tool to find current, specific information. Prefer official sources such \
as kkv.fi, kuluttajariita.fi, finlex.fi, traficom.fi and europa.eu.
- You may search several times, refining the query based on what you found. Stop searching \
once you have enough to answer.
- Each search result has an id such as [S3]. Cite claims with these ids. Never invent sources \
or URLs; only cite ids you have actually received.

Final answer (when you stop calling tools):
- Write in the same language as the user (usually Finnish), briefly and concretely.
- Say what the user is likely entitled to (with amounts if the law gives them), what \
information is still missing, and the next steps.
- Remind the user that this is not legal advice."""

FINAL_PROMPT = (
    "Hakukierrokset ovat loppuneet. Kirjoita nyt lopullinen vastaus "
    "jo löydettyjen lähteiden perusteella ja viittaa niihin tunnisteilla, kuten [S1]."
)

STUB_ANSWER = (
    "Tämä on kehitysvaiheen esimerkkivastaus. Lisää GEMINI_API_KEY, jotta agentti "
    "voi tutkia tilanteesi."
)

SEARCH_TOOL: dict[str, Any] = {
    "type": "function",
    "function": {
        "name": "search_web",
        "description": "Search the web with Exa and return relevant pages with excerpts.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "A specific natural-language search query.",
                },
                "include_domains": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Optional list of domains to restrict the search to.",
                },
            },
            "required": ["query"],
        },
    },
}


def handle_claim(description: str) -> ClaimResponse:
    """Research the user's claim and return an answer, its sources and a letter draft."""
    if not get_gemini_key():
        return _stub_response(description)
    found: list[Source] = []
    answer = _research(description, found)
    sources = _cited_sources(answer, found)
    return ClaimResponse(
        answer=answer,
        sources=sources,
        draft_letter=build_draft(description, answer, sources),
    )


def _research(description: str, found: list[Source]) -> str:
    """Let Gemini call search_web for up to MAX_ROUNDS rounds, then return its final answer."""
    messages: list[dict[str, Any]] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": description},
    ]
    for _ in range(MAX_ROUNDS):
        message = chat(messages, tools=[SEARCH_TOOL])
        if not message.tool_calls:
            return message.content or ""
        messages.append(message.model_dump(exclude_none=True))
        for call in message.tool_calls:
            messages.append(
                {"role": "tool", "tool_call_id": call.id, "content": _run_search(call, found)}
            )
    messages.append({"role": "user", "content": FINAL_PROMPT})
    return chat(messages, tools=[SEARCH_TOOL], tool_choice="none").content or ""


def _run_search(call: Any, found: list[Source]) -> str:
    """Execute one search_web tool call and format the results for the model."""
    try:
        args = json.loads(call.function.arguments or "{}")
    except json.JSONDecodeError:
        return "Virheelliset hakuparametrit."
    results = search_web(args.get("query", ""), args.get("include_domains"))
    lines = []
    for source in results:
        source_id = _remember(source, found)
        lines.append(f"[{source_id}] {source.title}\n{source.url}\n{source.quote or ''}")
    return "\n\n".join(lines) or "Ei tuloksia."


def _remember(source: Source, found: list[Source]) -> str:
    """Store a source once and return its stable id, e.g. 'S3'."""
    for index, known in enumerate(found):
        if known.url == source.url:
            return f"S{index + 1}"
    found.append(source)
    return f"S{len(found)}"


def _cited_sources(answer: str, found: list[Source]) -> list[Source]:
    """Return the sources the answer cites, or every found source if it cites none."""
    cited = {int(number) for number in re.findall(r"\[S(\d+)\]", answer)}
    selected = [source for index, source in enumerate(found, start=1) if index in cited]
    return selected or found


def _stub_response(description: str) -> ClaimResponse:
    """Return a deterministic response when Gemini is not configured."""
    sources = search_web(description)
    return ClaimResponse(
        answer=STUB_ANSWER,
        sources=sources,
        draft_letter=build_draft(description, STUB_ANSWER, sources),
    )
