"""Recognise the same job posted on several sites (title + employer, not URL)."""

import re

# Words that do not tell two jobs apart.
STOP_WORDS = {
    "oy", "oyj", "ab", "ltd", "ry", "rf", "inc", "finland", "suomi", "the", "ja", "and", "lle",
}


def tokens(text: str | None) -> set[str]:
    """Lowercase words of a title or employer, without site suffixes and filler words."""
    if not text:
        return set()
    text = text.split(" | ")[0]  # "Title | Duunitori"
    words = re.findall(r"[a-z0-9åäö]+", text.lower())
    return {word for word in words if word not in STOP_WORDS and len(word) > 1}


def same_job(title_a: str, employer_a: str | None, title_b: str, employer_b: str | None) -> bool:
    """True when two ads are very likely the same position."""
    words_a, words_b = tokens(title_a), tokens(title_b)
    if not words_a or not words_b:
        return False
    if not (words_a <= words_b or words_b <= words_a):
        return False
    employers_a, employers_b = tokens(employer_a), tokens(employer_b)
    if not employers_a or not employers_b:
        # Without an employer only an identical title counts as the same job.
        return words_a == words_b
    # The employer may appear in the other ad's title instead ("Assistentti, Firma Oy").
    return bool(employers_a & (employers_b | words_b) or employers_b & words_a)
