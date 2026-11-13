"""FastAPI application and transport routes."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .agent import handle_claim
from .schemas import ClaimRequest, ClaimResponse

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
    return handle_claim(request.description)
