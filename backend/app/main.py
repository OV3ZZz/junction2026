"""FastAPI application and transport routes."""

import logging
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .agent import handle_claim
from .config import get_allowed_origins
from .rate_limit import check_claim_limit
from .schemas import ClaimRequest, ClaimResponse

logger = logging.getLogger(__name__)

# In the deployed container the built frontend is copied here and served from the same origin.
STATIC_DIR = Path(__file__).resolve().parents[1] / "static"

app = FastAPI(title="Reklama API")
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


@app.post("/claim", response_model=ClaimResponse, dependencies=[Depends(check_claim_limit)])
def claim(request: ClaimRequest) -> ClaimResponse:
    """Analyze a consumer claim and return a draft for the user to review."""
    try:
        return handle_claim(request.description)
    except Exception as error:
        # Raising HTTPException keeps CORS headers, so the browser shows this message
        # instead of a generic "Failed to fetch".
        logger.exception("Claim handling failed")
        raise HTTPException(
            status_code=502, detail="Selvitys epäonnistui. Yritä hetken päästä uudelleen."
        ) from error


# Mounted last so the API routes above take precedence over static files.
if STATIC_DIR.is_dir():
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="frontend")
