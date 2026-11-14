"""FastAPI application and transport routes."""

import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .agent import handle_claim
from .schemas import ClaimRequest, ClaimResponse

logger = logging.getLogger(__name__)

app = FastAPI(title="Reklama API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    """Return a simple liveness response."""
    return {"status": "ok"}


@app.post("/claim", response_model=ClaimResponse)
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
