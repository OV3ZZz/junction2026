"""Agent loop skeleton for research-backed consumer claim assistance."""

from .draft import build_draft
from .exa_client import search_web
from .schemas import ClaimResponse

MAX_ROUNDS = 5


def handle_claim(description: str) -> ClaimResponse:
    """Return a scaffold response; TODO: implement the bounded LLM/Exa agent loop."""
    # TODO: Plan with the LLM, search via Exa, inspect results, and repeat up to MAX_ROUNDS.
    sources = search_web(description)
    answer = "Tämä on kehitysvaiheen esimerkkivastaus. Lisää tietoja, jotta tilanne voidaan arvioida."
    return ClaimResponse(
        answer=answer,
        sources=sources,
        draft_letter=build_draft(answer, sources),
    )
