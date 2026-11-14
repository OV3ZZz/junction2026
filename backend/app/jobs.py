"""Job search logic: raw user wish -> Exa deep search -> validated job ads."""

import json
from datetime import date
from typing import Any

from . import cache, deadline, exa_client
from .config import get_exa_key
from .dedupe import same_job
from .schemas import Job, ResponseLanguage, SeenJob

MAX_JOBS = 9  # the frontend shows three at a time

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
                    "deadline": {
                        "type": "string",
                        "description": "Application deadline as YYYY-MM-DD, or empty if none",
                    },
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


def build_query(
    area: str,
    wish: str,
    feedback: str | None = None,
    response_language: ResponseLanguage = "fi",
) -> str:
    """Pass the user's own words to Exa almost verbatim; Exa deep search expands them."""
    if response_language == "en":
        parts = [f"Open jobs matching this description: {wish.strip()}"]
        area_label = "Location"
    else:
        parts = [f"Avoimet työpaikat: {wish.strip()}"]
        area_label = "Alue"
    if area.strip():
        parts.append(f"{area_label}: {area.strip()}")
    if feedback and feedback.strip():
        parts.append(feedback.strip())
    return "\n".join(parts)


def system_prompt(response_language: ResponseLanguage = "fi") -> str:
    if response_language == "en":
        output_instructions = (
            "Write the job title, summary, and why in English. Translate titles and descriptions "
            "when needed, but keep employer names and official location names unchanged."
        )
    else:
        output_instructions = "Write the job title, summary, and why in Finnish."
    return (
        "Find single job advertisements in Finland that are still open for applications "
        f"(today is {date.today().isoformat()}) and fit the person's wish. Prefer the ad page "
        "itself on job boards or the employer's own careers page, not listing or search pages. "
        "Only include ads that are currently open. Exclude an ad if its page or source text says "
        "applications have closed or gives a closing date in the past, even if the exact deadline "
        "cannot be extracted. A missing deadline may be empty only when the ad still appears open. "
        "If open status is unclear, leave it out. List each position only "
        "once even if it is posted on several sites; prefer the employer's own page. "
        "If the wish is nonsensical (for example, 'asdfgh qwerty zxcv') or has no interpretable "
        "work-related skills or preferences, return an empty jobs list; never guess a role or "
        "default location. "
        f"Return up to {MAX_JOBS} jobs. {output_instructions} Write 'summary' (2 sentences about "
        "the duties) and 'why' (1 sentence explaining only how the job fits the person's stated "
        "skills or preferences). Do not mention deadlines, closing dates, or application status "
        "in 'why'; those belong only in 'deadline'. 'deadline' as YYYY-MM-DD or empty."
    )


def search_jobs(
    area: str,
    wish: str,
    exclude_urls: list[str],
    feedback: str | None = None,
    seen_jobs: list[SeenJob] | None = None,
    response_language: ResponseLanguage = "fi",
) -> list[Job]:
    """Return fresh job ads for the wish, skipping ads the user has already seen."""
    if not get_exa_key():
        if response_language == "en":
            return [
                job.model_copy(update={
                    "title": "Example job (stub)",
                    "employer": "Example Inc.",
                    "summary": "Development example. Set EXA_API_KEY to run a real search.",
                    "why": "Shown because no Exa API key is configured.",
                })
                for job in STUB_JOBS
            ]
        return [job.model_copy() for job in STUB_JOBS]
    skip = set(exclude_urls)
    kept: list[Job] = []
    previous = [(job.title, job.employer) for job in seen_jobs or []]
    query = build_query(area, wish, feedback, response_language)
    for job in _candidates(query, response_language):
        if job.url in skip or any(same_job(job.title, job.employer, *p) for p in previous):
            continue
        kept.append(job)
        previous.append((job.title, job.employer))
    return kept[:MAX_JOBS]


def _candidates(query: str, response_language: ResponseLanguage = "fi") -> list[Job]:
    """Valid, still-open jobs for a query, cached for repeat searches."""
    cache_key = f"prompt-v2:{response_language}:{query}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached
    response = exa_client.deep_search(query, system_prompt(response_language), JOB_SCHEMA)
    allowed = {result.url for result in response.results}
    jobs = _valid_jobs(_output_jobs(response), allowed)
    cache.put(cache_key, jobs)
    return jobs


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


def _valid_jobs(items: list[dict[str, Any]], allowed: set[str]) -> list[Job]:
    """Keep jobs whose URL is a real Exa result and whose deadline has not passed."""
    jobs: list[Job] = []
    seen: set[str] = set()
    today = date.today()
    for item in items:
        url = item.get("url") or ""
        if url not in allowed or url in seen or not item.get("title"):
            continue
        if deadline.is_expired(item.get("deadline"), today):
            continue
        seen.add(url)
        jobs.append(
            Job(
                title=item["title"],
                employer=item.get("employer") or None,
                location=item.get("location") or None,
                url=url,
                deadline=deadline.display(item.get("deadline")),
                summary=item.get("summary") or "",
                why=item.get("why") or None,
            )
        )
    return jobs

