"""Environment configuration for optional live API integrations."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")


def get_api_keys() -> tuple[str | None, str | None]:
    """Return configured Exa and OpenAI keys, raising a clear error if incomplete."""
    exa_key = os.getenv("EXA_API_KEY") or None
    openai_key = os.getenv("OPENAI_API_KEY") or None
    if exa_key and not openai_key:
        raise RuntimeError("OPENAI_API_KEY is required when EXA_API_KEY enables live mode.")
    if openai_key and not exa_key:
        raise RuntimeError("EXA_API_KEY is required when OPENAI_API_KEY enables live mode.")
    return exa_key, openai_key


def get_openai_model() -> str:
    """Return the configured model name or a development default."""
    return os.getenv("OPENAI_MODEL", "gpt-4o-mini")
