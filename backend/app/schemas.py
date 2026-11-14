"""API schemas shared by the backend and frontend contract."""

from typing import Annotated, Literal

from pydantic import BaseModel, Field, StringConstraints

ResponseLanguage = Literal["fi", "en"]
JobStatus = Literal["open", "unknown"]
SearchWish = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class SeenJob(BaseModel):
    """A job already shown, so the same position on another site is skipped."""

    title: str
    employer: str | None = None


class JobSearchRequest(BaseModel):
    """A job seeker's area and free-form wish, plus what to skip on a refresh."""

    area: str = ""
    wish: SearchWish
    exclude_urls: list[str] = Field(default_factory=list)
    seen_jobs: list[SeenJob] = Field(default_factory=list)
    feedback: str | None = None
    response_language: ResponseLanguage = "fi"


class Job(BaseModel):
    """One job ad found by Exa. The url always comes from an Exa result."""

    title: str
    employer: str | None = None
    location: str | None = None
    url: str
    deadline: str | None = None
    summary: str
    why: str | None = None
    status: JobStatus = "open"


class JobSearchResponse(BaseModel):
    """A batch of job ads; the frontend shows them a few at a time."""

    jobs: list[Job]

