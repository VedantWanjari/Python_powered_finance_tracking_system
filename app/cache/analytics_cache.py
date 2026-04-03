"""
app/cache/analytics_cache.py
─────────────────────────────
Simple in-process TTL cache for analytics results.

Why not Redis?
  • This system targets a single-process deployment (student assignment).
  • Adding Redis would require an extra infrastructure dependency.
  • The interface is identical to what a Redis adapter would expose,
    so swapping in Redis later is a one-file change.

Thread safety:
  Python's GIL makes dict reads/writes atomic for simple key operations,
  but we use a threading.Lock for the get+check+set sequence anyway so
  the code is correct even if the GIL is removed in future Python versions.
"""

import time
import threading
import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)


class AnalyticsCache:
    """
    Key-value store with per-entry TTL (time-to-live).

    Each entry is stored as (value, expiry_timestamp).
    An entry is considered "hit" only if current time < expiry.
    """

    def __init__(self, default_ttl: int = 300) -> None:
        """
        Args:
            default_ttl: Seconds before a cached entry expires (default 5 min).
        """
        self._store: dict = {}          # { key: (value, expiry_float) }
        self._lock = threading.Lock()   # guards concurrent get/set operations
        self.default_ttl = default_ttl  # used when caller omits ttl argument

    # ── Public interface ──────────────────────────────────────────────────

    def get(self, key: str) -> Optional[Any]:
        """
        Return the cached value for *key*, or None if missing / expired.

        Args:
            key: Cache key string.

        Returns:
            Cached value or None.
        """
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None                         # cache miss

            value, expiry = entry
            if time.monotonic() > expiry:
                # Entry has expired – remove it to keep the dict lean
                del self._store[key]
                logger.debug("Cache EXPIRED: %s", key)
                return None                         # treat as miss

            logger.debug("Cache HIT: %s", key)
            return value

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Store *value* under *key* for *ttl* seconds.

        Args:
            key:   Cache key string.
            value: Any JSON-serialisable object.
            ttl:   Seconds until expiry; uses default_ttl when omitted.
        """
        ttl = ttl if ttl is not None else self.default_ttl
        expiry = time.monotonic() + ttl   # absolute expiry time
        with self._lock:
            self._store[key] = (value, expiry)
        logger.debug("Cache SET: %s (ttl=%ss)", key, ttl)

    def invalidate(self, key: str) -> None:
        """Remove a single cache entry (e.g. after a transaction is updated)."""
        with self._lock:
            self._store.pop(key, None)   # pop(key, None) is safe if key missing
        logger.debug("Cache INVALIDATED: %s", key)

    def invalidate_user(self, user_id: int) -> None:
        """
        Invalidate all cache entries that belong to *user_id*.

        Analytics cache keys follow the pattern "<user_id>:<scope>", so we
        can sweep all keys with the matching prefix after a data change.

        Args:
            user_id: The user whose cached analytics are now stale.
        """
        prefix = f"{user_id}:"
        with self._lock:
            stale_keys = [k for k in self._store if k.startswith(prefix)]
            for key in stale_keys:
                del self._store[key]
        if stale_keys:
            logger.debug("Cache INVALIDATED %d keys for user %s", len(stale_keys), user_id)

    def clear(self) -> None:
        """Flush the entire cache (used in tests)."""
        with self._lock:
            self._store.clear()


# ── Module-level singleton ────────────────────────────────────────────────────
# Shared across the whole process; import this object wherever caching is needed
analytics_cache = AnalyticsCache()
