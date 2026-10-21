"""Token-bucket rate limiting per user (or per IP before sign-in).

In-process buckets suit a single API instance. With several instances, put the limit in the
reverse proxy or swap this class for a Redis-backed one with the same interface.
"""

import threading
import time

from fastapi import HTTPException, Request, status


class TokenBucketLimiter:
    def __init__(self, per_minute: int, burst: int | None = None) -> None:
        self.rate = per_minute / 60.0
        self.capacity = float(burst or per_minute)
        self._buckets: dict[str, tuple[float, float]] = {}
        self._lock = threading.Lock()

    def allow(self, key: str, cost: float = 1.0) -> tuple[bool, float]:
        now = time.monotonic()
        with self._lock:
            tokens, last = self._buckets.get(key, (self.capacity, now))
            tokens = min(self.capacity, tokens + (now - last) * self.rate)
            if tokens >= cost:
                self._buckets[key] = (tokens - cost, now)
                return True, 0.0
            self._buckets[key] = (tokens, now)
            return False, (cost - tokens) / self.rate

    def check(self, request: Request, cost: float = 1.0) -> None:
        key = getattr(request.state, "user_id", None) or (request.client.host if request.client else "anon")
        ok, retry = self.allow(str(key), cost)
        if not ok:
            raise HTTPException(
                status.HTTP_429_TOO_MANY_REQUESTS,
                "Too many requests. Wait a moment and try again.",
                headers={"Retry-After": str(max(1, int(retry + 0.5)))},
            )
