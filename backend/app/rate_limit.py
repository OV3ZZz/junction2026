"""Global hourly limit for /claim so a public demo cannot drain the API credits.

The limit is global rather than per IP because judges at the venue share one network.
"""

import threading
import time
from collections import deque

from fastapi import HTTPException

from .config import get_max_claims_per_hour

WINDOW_SECONDS = 3600

_lock = threading.Lock()
_recent_claims: deque[float] = deque()


def check_claim_limit() -> None:
    """Record one claim, or raise 429 when the hourly limit is already used up."""
    limit = get_max_claims_per_hour()
    if limit <= 0:
        return
    now = time.monotonic()
    with _lock:
        while _recent_claims and now - _recent_claims[0] > WINDOW_SECONDS:
            _recent_claims.popleft()
        if len(_recent_claims) >= limit:
            raise HTTPException(
                status_code=429,
                detail="Palvelu on juuri nyt ruuhkainen. Yritä hetken päästä uudelleen.",
            )
        _recent_claims.append(now)


def reset() -> None:
    """Forget recorded claims (used by tests)."""
    with _lock:
        _recent_claims.clear()
