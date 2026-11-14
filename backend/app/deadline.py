"""Turn the deadline text Exa extracts into a date, so closed ads can be dropped."""

import re
from datetime import date

ISO_DATE = re.compile(r"(\d{4})-(\d{1,2})-(\d{1,2})")
FINNISH_DATE = re.compile(r"(\d{1,2})\.(\d{1,2})\.(\d{4})")
MAX_TEXT_LENGTH = 30  # longer free text ("hakuajankohta; tehtävä ...") is not shown


def parse(text: str | None) -> date | None:
    """First date in the text (2026-11-19 or 19.11.2026), or None."""
    if not text:
        return None
    if match := ISO_DATE.search(text):
        year, month, day = (int(part) for part in match.groups())
    elif match := FINNISH_DATE.search(text):
        day, month, year = (int(part) for part in match.groups())
    else:
        return None
    try:
        return date(year, month, day)
    except ValueError:
        return None


def is_expired(text: str | None, today: date) -> bool:
    """True when the ad states a deadline that has already passed."""
    deadline = parse(text)
    return deadline is not None and deadline < today


def display(text: str | None) -> str | None:
    """Short Finnish date for the card, short free text as is ("Haetaan heti"), else None."""
    deadline = parse(text)
    if deadline:
        return f"{deadline.day}.{deadline.month}.{deadline.year}"
    if text and len(text.strip()) <= MAX_TEXT_LENGTH:
        return text.strip()
    return None
