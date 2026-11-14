"""Global hourly limit for job searches so a demo cannot drain the API credits.

The limit is global rather than per IP because judges at the venue share one network.
"""

import threading
import time
from collections import deque

from fastapi import HTTPException

from .config import get_max_searches_per_hour

WINDOW_SECONDS = 3600

_lock = threading.Lock()
_recent_searches: deque[float] = deque()


def check_search_limit() -> None:
    """Record one search, or raise 429 when the hourly limit is already used up."""
    limit = get_max_searches_per_hour()
    if limit <= 0:
        return
    now = time.monotonic()
    with _lock:
        while _recent_searches and now - _recent_searches[0] > WINDOW_SECONDS:
            _recent_searches.popleft()
        if len(_recent_searches) >= limit:
            raise HTTPException(
                status_code=429,
                detail="Palvelu on juuri nyt ruuhkainen. Yritä hetken päästä uudelleen.",
            )
        _recent_searches.append(now)


def reset() -> None:
    """Forget recorded searches (used by tests)."""
    with _lock:
        _recent_searches.clear()
