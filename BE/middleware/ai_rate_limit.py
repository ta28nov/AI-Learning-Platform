"""
Rate limiting for AI-heavy endpoints — tránh burst gây quota/429 và tắc nghẽn.
In-memory sliding window theo user (JWT sub) hoặc IP ẩn danh.
"""

import time
from collections import defaultdict, deque
from typing import Deque, Dict, Optional, Tuple

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from config.config import get_settings

# path prefix (sau /api/v1) -> max requests per window
AI_ROUTE_LIMITS: Dict[str, Tuple[int, int]] = {
    "/assessments/generate": (5, 60),
    "/courses/from-prompt": (3, 60),
    "/chat/course": (30, 60),
    "/ai/": (10, 60),
}

_buckets: Dict[str, Deque[float]] = defaultdict(deque)


def _client_key(request: Request) -> str:
    auth = request.headers.get("authorization") or ""
    if auth.lower().startswith("bearer "):
        return f"user:{auth[7:36]}"
    forwarded = request.headers.get("x-forwarded-for")
    ip = (forwarded.split(",")[0].strip() if forwarded else None) or (
        request.client.host if request.client else "anon"
    )
    return f"ip:{ip}"


def _match_ai_limit(path: str) -> Optional[Tuple[str, int, int]]:
    """Return (route_key, max_calls, window_seconds) or None."""
    for prefix, (limit, window) in AI_ROUTE_LIMITS.items():
        if prefix in path:
            return prefix, limit, window
    return None


class AIRateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method != "POST":
            return await call_next(request)

        path = request.url.path
        if "/api/v1" not in path:
            return await call_next(request)

        matched = _match_ai_limit(path)
        if not matched:
            settings = get_settings()
            global_limit = getattr(settings, "rate_limit_per_minute", 100)
            route_key, max_calls, window = "__global__", global_limit, 60
        else:
            route_key, max_calls, window = matched

        now = time.time()
        bucket_id = f"{_client_key(request)}:{route_key}"
        q = _buckets[bucket_id]
        while q and q[0] <= now - window:
            q.popleft()

        if len(q) >= max_calls:
            retry_after = max(1, int(window - (now - q[0]))) if q else window
            return JSONResponse(
                status_code=429,
                content={
                    "detail": (
                        f"Quá nhiều yêu cầu AI ({max_calls}/{window}s). "
                        "Vui lòng thử lại sau."
                    )
                },
                headers={"Retry-After": str(retry_after)},
            )

        q.append(now)
        response: Response = await call_next(request)
        return response
