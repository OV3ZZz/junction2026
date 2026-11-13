"""Exa search adapter with deterministic data for local scaffold development."""

from .schemas import Source

_STUB_SOURCES = [
    Source(
        title="Consumer claim research placeholder",
        url="https://example.com/consumer-claim-guidance",
        quote="Stub source for local development; replace with Exa results in live mode.",
    )
]


def search_web(query: str, include_domains: list[str] | None = None) -> list[Source]:
    """Search Exa for relevant sources; return fixed fake data without credentials."""
    del query, include_domains
    # TODO: Call Exa when credentials and live agent flow are enabled.
    return [source.model_copy() for source in _STUB_SOURCES]
