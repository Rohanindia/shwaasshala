import time
from typing import Any, Optional
import threading

class SimpleCache:
    def __init__(self, default_ttl: int = 600):
        self.default_ttl = default_ttl
        self._store: dict[str, tuple[float, Any]] = {}
        self._lock = threading.Lock()

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            entry = self._store.get(key)
            if not entry:
                return None
            expires_at, val = entry
            if time.time() > expires_at:
                del self._store[key]
                return None
            return val

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        duration = ttl if ttl is not None else self.default_ttl
        with self._lock:
            self._store[key] = (time.time() + duration, value)

    def clear(self) -> None:
        with self._lock:
            self._store.clear()

cache = SimpleCache()
