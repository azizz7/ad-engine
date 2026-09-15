"""
Minimal in-memory fixed-window rate limiter.

This is intentionally simple (no Redis, no extra dependency) and is only
meant to blunt naive brute-force attempts against the login endpoint on a
single-process deployment. For a multi-process/production deployment,
replace with a shared store (e.g. Redis) behind the same interface.
"""
import time
from collections import defaultdict

from fastapi import HTTPException, Request, status


class FixedWindowRateLimiter:
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._hits: dict[str, list[float]] = defaultdict(list)

    def check(self, key: str) -> None:
        now = time.monotonic()
        window_start = now - self.window_seconds
        hits = [t for t in self._hits[key] if t > window_start]
        if len(hits) >= self.max_requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many attempts. Please try again later.",
            )
        hits.append(now)
        self._hits[key] = hits


login_rate_limiter = FixedWindowRateLimiter(max_requests=10, window_seconds=60)


def enforce_login_rate_limit(request: Request) -> None:
    client_ip = request.client.host if request.client else "unknown"
    login_rate_limiter.check(client_ip)
