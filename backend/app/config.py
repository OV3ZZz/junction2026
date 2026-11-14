"""Environment configuration for optional live API integrations."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

# Gemini offers an OpenAI-compatible endpoint, so the `openai` package can talk to it.
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
DEFAULT_GEMINI_MODEL = "gemini-3.8-flash"


def get_exa_key() -> str | None:
    """Return the Exa key, or None to use stub search results."""
    return os.getenv("EXA_API_KEY") or None


def get_gemini_key() -> str | None:
    """Return the Gemini key, or None to skip the LLM agent loop."""
    return os.getenv("GEMINI_API_KEY") or None


def get_gemini_model() -> str:
    """Return the configured Gemini model name or a sensible default."""
    return os.getenv("GEMINI_MODEL") or DEFAULT_GEMINI_MODEL
