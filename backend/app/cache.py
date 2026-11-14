"""Small in-memory TTL cache so repeated demo searches answer instantly and save Exa credits."""

import threading
import time
from typing import Any

TTL_SECONDS = 3600
MAX_ENTRIES = 200

_lock = threading.Lock()
_entries: dict[str, tuple[float, Any]] = {}


def get(key: str) -> Any | None:
    """Return a cached value that is younger than TTL_SECONDS, else None."""
    with _lock:
        entry = _entries.get(key)
        if entry is None or time.monotonic() - entry[0] > TTL_SECONDS:
            _entries.pop(key, None)
            return None
        return entry[1]


def put(key: str, value: Any) -> None:
    """Store a value, dropping the oldest entry when the cache is full."""
    with _lock:
        if len(_entries) >= MAX_ENTRIES:
            oldest = min(_entries, key=lambda k: _entries[k][0])
            del _entries[oldest]
        _entries[key] = (time.monotonic(), value)


def clear() -> None:
    """Forget everything (used by tests)."""
    with _lock:
        _entries.clear()
