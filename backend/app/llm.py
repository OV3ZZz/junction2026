"""Thin wrapper around Gemini's OpenAI-compatible chat API."""

from typing import Any

from openai import OpenAI

from .config import GEMINI_BASE_URL, get_gemini_key, get_gemini_model


def chat(
    messages: list[dict[str, Any]],
    tools: list[dict[str, Any]] | None = None,
    tool_choice: str | None = None,
) -> Any:
    """Send the conversation to Gemini and return the assistant message."""
    client = OpenAI(api_key=get_gemini_key(), base_url=GEMINI_BASE_URL)
    options: dict[str, Any] = {}
    if tools:
        options["tools"] = tools
    if tool_choice:
        options["tool_choice"] = tool_choice
    response = client.chat.completions.create(
        model=get_gemini_model(), messages=messages, **options
    )
    return response.choices[0].message
