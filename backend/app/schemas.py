"""API schemas shared by the backend and frontend contract."""

from pydantic import BaseModel, Field


class SeenJob(BaseModel):
    """A job already shown, so the same position on another site is skipped."""

    title: str
    employer: str | None = None


class JobSearchRequest(BaseModel):
    """A job seeker's area and free-form wish, plus what to skip on a refresh."""

    area: str = ""
    wish: str = Field(min_length=1)
    exclude_urls: list[str] = Field(default_factory=list)
    seen_jobs: list[SeenJob] = Field(default_factory=list)
    feedback: str | None = None


class Job(BaseModel):
    """One job ad found by Exa. The url always comes from an Exa result."""

    title: str
    employer: str | None = None
    location: str | None = None
    url: str
    deadline: str | None = None
    summary: str
    why: str | None = None


class JobSearchResponse(BaseModel):
    """A batch of job ads; the frontend shows them a few at a time."""

    jobs: list[Job]

