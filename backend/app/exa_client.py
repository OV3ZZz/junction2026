"""Exa search adapter with deterministic data for local development."""

from typing import Any

from exa_py import Exa

from .config import get_exa_key
from .schemas import Source

NUM_RESULTS = 2
QUOTE_MAX_CHARS = 600

_STUB_SOURCES = [
    Source(
        title="Consumer claim research placeholder",
        url="https://example.com/consumer-claim-guidance",
        quote="Stub source for local development; replace with Exa results in live mode.",
    )
]


def search_web(query: str, include_domains: list[str] | None = None) -> list[Source]:
    """Search Exa for relevant sources; return fixed fake data without credentials."""
    api_key = get_exa_key()
    if not api_key:
        return [source.model_copy() for source in _STUB_SOURCES]
    options: dict[str, Any] = {"num_results": NUM_RESULTS, "text": {"max_characters": 2000}}
    if include_domains:
        options["include_domains"] = include_domains
    response = Exa(api_key=api_key).search_and_contents(query, **options)
    return [_to_source(result) for result in response.results]


def _to_source(result: Any) -> Source:
    """Convert one Exa result into our Source schema."""
    text = " ".join((result.text or "").split())
    return Source(title=result.title or result.url, url=result.url, quote=text[:QUOTE_MAX_CHARS])
