"""Thin adapter around the Exa SDK so business logic stays testable."""

from datetime import date, timedelta
from typing import Any

from exa_py import Exa

from .config import get_exa_key

# Job ads older than this are usually closed already.
FRESH_DAYS = 21
NUM_RESULTS = 15
HIGHLIGHT_CHARS = 400
# These aggregators keep stale ads online and may not expose their closed status reliably.
EXCLUDED_DOMAINS = ["bebee.com", "jooble.org", "careerjet.fi", "jobleads.com", "drjobpro.com"]


def _client() -> Exa:
    return Exa(api_key=get_exa_key())


def _since() -> str:
    return (date.today() - timedelta(days=FRESH_DAYS)).isoformat()


def deep_search(query: str, system_prompt: str, output_schema: dict[str, Any]) -> Any:
    """Exa deep search: Exa expands the raw query itself and returns structured output."""
    return _client().search(
        query,
        type="deep",
        num_results=NUM_RESULTS,
        exclude_domains=EXCLUDED_DOMAINS,
        start_published_date=_since(),
        system_prompt=system_prompt,
        output_schema=output_schema,
        contents={"highlights": {"max_characters": HIGHLIGHT_CHARS}},
    )

