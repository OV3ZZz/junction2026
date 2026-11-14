"""Environment configuration for optional live API integrations."""

import os
from pathlib import Path

from dotenv import load_dotenv

# override=True: the local .env wins over stale values already in the shell, e.g. an old key
# that VS Code injected into the terminal ("python.terminal.useEnvFile"). On Render there is
# no .env file, so the host's environment variables are used as is.
load_dotenv(Path(__file__).resolve().parents[2] / ".env", override=True)

DEFAULT_ALLOWED_ORIGINS = "http://localhost:5173,http://127.0.0.1:5173"
DEFAULT_MAX_SEARCHES_PER_HOUR = 120


def get_exa_key() -> str | None:
    """Return the Exa key, or None to use stub job ads."""
    return os.getenv("EXA_API_KEY") or None


def get_allowed_origins() -> list[str]:
    """Return browser origins allowed to call the API."""
    raw = os.getenv("ALLOWED_ORIGINS") or DEFAULT_ALLOWED_ORIGINS
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


def get_max_searches_per_hour() -> int:
    """Return the global search limit per hour that protects API credits; 0 disables it."""
    value = os.getenv("MAX_SEARCHES_PER_HOUR")
    return int(value) if value else DEFAULT_MAX_SEARCHES_PER_HOUR
