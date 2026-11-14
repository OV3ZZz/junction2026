"""FastAPI application and transport routes."""

import logging
from collections.abc import Callable
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import get_allowed_origins
from .jobs import search_jobs
from .rate_limit import check_search_limit
from .schemas import Job, JobSearchRequest, JobSearchResponse

logger = logging.getLogger(__name__)

# In the Docker image the built frontend is copied here and served from the same origin.
STATIC_DIR = Path(__file__).resolve().parents[1] / "static"

app = FastAPI(title="Job search API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    """Return a simple liveness response."""
    return {"status": "ok"}


@app.post("/jobs/search", response_model=JobSearchResponse,
          dependencies=[Depends(check_search_limit)])
def jobs_search(request: JobSearchRequest) -> JobSearchResponse:
    """Find fresh job ads that match the user's area and free-form wish."""
    return _respond(lambda: search_jobs(
        request.area, request.wish, request.exclude_urls, request.feedback))


def _respond(find: Callable[[], list[Job]]) -> JobSearchResponse:
    # Raising HTTPException keeps CORS headers, so the browser shows this message
    # instead of a generic "Failed to fetch".
    try:
        return JobSearchResponse(jobs=find())
    except Exception as error:
        logger.exception("Job search failed")
        raise HTTPException(
            status_code=502, detail="Haku epäonnistui. Yritä hetken päästä uudelleen."
        ) from error


# Mounted last so the API routes above take precedence over static files.
if STATIC_DIR.is_dir():
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="frontend")
