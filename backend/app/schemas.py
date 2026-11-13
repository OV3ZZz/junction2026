"""API schemas shared by the backend and frontend contract."""

from pydantic import BaseModel, Field


class ClaimRequest(BaseModel):
    """A consumer's description of a potential claim."""

    description: str = Field(min_length=1)


class Source(BaseModel):
    """A source supporting the claim assessment."""

    title: str
    url: str
    quote: str | None = None


class ClaimResponse(BaseModel):
    """Research result and user-reviewable complaint draft."""

    answer: str
    sources: list[Source]
    draft_letter: str
