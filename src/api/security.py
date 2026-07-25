"""Basic Auth + per-IP rate limiting for the public hosted demo.

Both are opt-in / scoped so local dev and tests are unaffected:

- ``BasicAuthMiddleware`` only checks credentials when both
  ``DEMO_BASIC_AUTH_USER`` and ``DEMO_BASIC_AUTH_PASS`` are set — unset
  (the default for local dev and the test suite) means no gate at all.
- ``RateLimitMiddleware`` always runs, but only counts requests against
  the routes that actually spend Anthropic/Voyage credits per click.
"""

from __future__ import annotations

import base64
import binascii
import os
import re
import secrets
import time
from collections import defaultdict

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

RATE_LIMITED_PATHS = (
    re.compile(r"^/chat$"),
    re.compile(r"^/chat/stream$"),
    re.compile(r"^/workflows/[^/]+/run$"),
    re.compile(r"^/workflows/[^/]+/stream$"),
    re.compile(r"^/briefs/generate$"),
)

# Generous enough for a live pitch demo (a handful of chat/workflow
# clicks per visitor) while capping the blast radius if the link/password
# gets shared beyond the intended audience.
RATE_LIMIT_MAX_REQUESTS = 30
RATE_LIMIT_WINDOW_SECONDS = 3600  # 1 hour


def _is_rate_limited_path(path: str) -> bool:
    return any(p.match(path) for p in RATE_LIMITED_PATHS)


class BasicAuthMiddleware(BaseHTTPMiddleware):
    """Gates the whole app (including the static UI and /admin/*)."""

    async def dispatch(self, request: Request, call_next):
        user = os.environ.get("DEMO_BASIC_AUTH_USER", "")
        password = os.environ.get("DEMO_BASIC_AUTH_PASS", "")
        if not user or not password:
            return await call_next(request)

        if _credentials_match(request.headers.get("authorization", ""), user, password):
            return await call_next(request)

        return Response(
            status_code=401,
            headers={"WWW-Authenticate": 'Basic realm="Graph HVAC demo"'},
        )


def _credentials_match(auth_header: str, user: str, password: str) -> bool:
    if not auth_header.startswith("Basic "):
        return False
    try:
        decoded = base64.b64decode(auth_header[len("Basic "):]).decode("utf-8")
    except (binascii.Error, UnicodeDecodeError):
        return False
    got_user, sep, got_pass = decoded.partition(":")
    if not sep:
        return False
    return secrets.compare_digest(got_user, user) and secrets.compare_digest(got_pass, password)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Per-IP cap on the LLM-calling routes only.

    In-memory by design: correct for a single always-on machine
    (``min_machines_running=1``), won't survive a restart or scale past
    one instance. Accepted tradeoff for a pitch demo, not a production
    guarantee.
    """

    def __init__(
        self,
        app,
        max_requests: int = RATE_LIMIT_MAX_REQUESTS,
        window_seconds: int = RATE_LIMIT_WINDOW_SECONDS,
    ) -> None:
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._hits: dict[str, list[float]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        if not _is_rate_limited_path(request.url.path):
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        now = time.monotonic()
        cutoff = now - self.window_seconds
        hits = self._hits[client_ip]
        while hits and hits[0] < cutoff:
            hits.pop(0)

        if len(hits) >= self.max_requests:
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded. Try again later."},
            )

        hits.append(now)
        return await call_next(request)
