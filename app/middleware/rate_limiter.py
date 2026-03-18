"""Sliding-window rate limiter middleware."""

from __future__ import annotations
import time, logging
from collections import deque
from typing import Dict, Deque
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)
WINDOW = 60
GLOBAL_LIMIT = 20
ANALYZE_LIMIT = 5

class RateLimiterMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self._buckets: Dict[str, Deque[float]] = {}

    async def dispatch(self, request: Request, call_next):
        ip = self._get_ip(request)
        is_analyze = request.url.path.startswith("/analyze/")
        key = f"{ip}:{'analyze' if is_analyze else 'global'}"
        limit = ANALYZE_LIMIT if is_analyze else GLOBAL_LIMIT

        if not self._allow(key, limit):
            return JSONResponse(
                status_code=429,
                content={"detail": f"Rate limit exceeded. Max {limit} requests per {WINDOW}s."},
                headers={"Retry-After": str(WINDOW)},
            )
        return await call_next(request)

    def _allow(self, key: str, limit: int) -> bool:
        now = time.time()
        if key not in self._buckets:
            self._buckets[key] = deque()
        bucket = self._buckets[key]
        while bucket and bucket[0] < now - WINDOW:
            bucket.popleft()
        if len(bucket) >= limit:
            return False
        bucket.append(now)
        return True

    @staticmethod
    def _get_ip(request: Request) -> str:
        fwd = request.headers.get("X-Forwarded-For")
        if fwd:
            return fwd.split(",")[0].strip()
        return request.client.host if request.client else "unknown"
