import time
import threading
import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)

class AnalyticsCache:

    def __init__(self, default_ttl: int = 300) -> None:
        self._store: dict = {}
        self._lock = threading.Lock()
        self.default_ttl = default_ttl

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None

            value, expiry = entry
            if time.monotonic() > expiry:
                del self._store[key]
                logger.debug("Cache EXPIRED: %s", key)
                return None

            logger.debug("Cache HIT: %s", key)
            return value

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        ttl = ttl if ttl is not None else self.default_ttl
        expiry = time.monotonic() + ttl
        with self._lock:
            self._store[key] = (value, expiry)
        logger.debug("Cache SET: %s (ttl=%ss)", key, ttl)

    def invalidate(self, key: str) -> None:
        with self._lock:
            self._store.pop(key, None)
        logger.debug("Cache INVALIDATED: %s", key)

    def invalidate_user(self, user_id: int) -> None:
        prefix = f"{user_id}:"
        with self._lock:
            stale_keys = [k for k in self._store if k.startswith(prefix)]
            for key in stale_keys:
                del self._store[key]
        if stale_keys:
            logger.debug("Cache INVALIDATED %d keys for user %s", len(stale_keys), user_id)

    def clear(self) -> None:
        with self._lock:
            self._store.clear()

analytics_cache = AnalyticsCache()
