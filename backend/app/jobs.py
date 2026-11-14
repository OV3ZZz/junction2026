"""Job search logic: raw user wish -> Exa deep search -> validated job ads."""

import json
from datetime import date
from typing import Any

from . import exa_client
from .config import get_exa_key
from .schemas import Job

MAX_JOBS = 9  # the frontend shows three at a time
MIN_JOBS = 6  # below this, fill up with plain Exa results
NOT_JOB_ADS = ("linkedin.com/in/",)  # profiles, not ads

JOB_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "jobs": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "employer": {"type": "string"},
                    "location": {"type": "string"},
                    "url": {"type": "string"},
                    "deadline": {"type": "string"},
                    "summary": {"type": "string"},
                    "why": {"type": "string"},
                },
            },
        }
    },
    "required": ["jobs"],
}

STUB_JOBS = [
    Job(
        title="Esimerkkityöpaikka (stub)",
        employer="Esimerkki Oy",
        location="Tampere",
        url="https://example.com/job/1",
        deadline=None,
        summary="Kehitystilan esimerkki. Lisää EXA_API_KEY, niin haku tehdään oikeasti.",
        why="Näytetään, koska Exa-avainta ei ole asetettu.",
    )
]


def build_query(area: str, wish: str, feedback: str | None = None) -> str:
    """Pass the user's own words to Exa almost verbatim; Exa deep search expands them."""
    parts = [f"Avoimet työpaikat: {wish.strip()}"]
    if area.strip():
        parts.append(f"Alue: {area.strip()}")
    if feedback and feedback.strip():
        parts.append(feedback.strip())
    return "\n".join(parts)


def system_prompt() -> str:
    return (
        "Find single job advertisements in Finland that are still open for applications "
        f"(today is {date.today().isoformat()}) and fit the person's wish. Prefer the ad page "
        "itself on job boards or the employer's own careers page, not listing or search pages. "
        f"Return up to {MAX_JOBS} jobs. Write 'summary' (2 sentences about the duties) and 'why' "
        "(1 sentence on why it fits the wish) in Finnish. 'deadline' as written in the ad, or empty."
    )


def search_jobs(
    area: str, wish: str, exclude_urls: list[str], feedback: str | None = None
) -> list[Job]:
    """Return fresh job ads for the wish, skipping ads the user has already seen."""
    if not get_exa_key():
        return [job.model_copy() for job in STUB_JOBS]
    response = exa_client.deep_search(
        build_query(area, wish, feedback), system_prompt(), JOB_SCHEMA
    )
    allowed = {result.url for result in response.results}
    found = _valid_jobs(_output_jobs(response), allowed, set(exclude_urls))
    return _top_up(found, response.results, set(exclude_urls))


def similar_jobs(area: str, wish: str, liked: Job, exclude_urls: list[str]) -> list[Job]:
    """Return ads like one the user liked, still respecting their original wish."""
    note = f"Etsi lisää tämän kaltaisia: {liked.title}. {liked.summary}"
    return search_jobs(area, wish, exclude_urls + [liked.url], note)


def _output_jobs(response: Any) -> list[dict[str, Any]]:
    """Read the structured jobs list from Exa's deep search output."""
    content = response.output.content if response.output else None
    if isinstance(content, str):
        try:
            content = json.loads(content)
        except json.JSONDecodeError:
            return []
    if not isinstance(content, dict):
        return []
    return [item for item in content.get("jobs", []) if isinstance(item, dict)]


def _valid_jobs(items: list[dict[str, Any]], allowed: set[str], skip: set[str]) -> list[Job]:
    """Keep jobs whose URL is a real Exa result and not already seen; drop duplicates."""
    jobs: list[Job] = []
    seen: set[str] = set()
    for item in items:
        url = item.get("url") or ""
        if url not in allowed or url in skip or url in seen or not item.get("title"):
            continue
        seen.add(url)
        jobs.append(
            Job(
                title=item["title"],
                employer=item.get("employer") or None,
                location=item.get("location") or None,
                url=url,
                deadline=item.get("deadline") or None,
                summary=item.get("summary") or "",
                why=item.get("why") or None,
            )
        )
    return jobs[:MAX_JOBS]


def _top_up(jobs: list[Job], results: list[Any], skip: set[str]) -> list[Job]:
    """Deep search output sometimes lists only a few jobs; fill up from the raw Exa results."""
    if len(jobs) >= MIN_JOBS:
        return jobs
    taken = {job.url for job in jobs} | skip
    extra = [
        _result_to_job(result) for result in results
        if result.url not in taken and not any(part in result.url for part in NOT_JOB_ADS)
    ]
    return (jobs + extra)[:MAX_JOBS]


def _result_to_job(result: Any) -> Job:
    """Turn a plain Exa result into a job card using its highlights as the summary."""
    summary = " … ".join(" ".join(h.split()) for h in (result.highlights or []))
    return Job(title=result.title or result.url, url=result.url, summary=summary)
