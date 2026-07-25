"""Tests for the demo-only Basic Auth + rate limiting middleware.

Uses standalone Starlette test apps (not the shared ``src.api.main.app``
singleton) so rate-limit state from these tests can never leak into the
real chat/workflow test cases in the rest of the suite.
"""

from __future__ import annotations

import base64

from starlette.applications import Starlette
from starlette.responses import PlainTextResponse
from starlette.routing import Route
from starlette.testclient import TestClient

from src.api.security import BasicAuthMiddleware, RateLimitMiddleware


async def _ok(request):
    return PlainTextResponse("ok")


def _basic_auth_app() -> Starlette:
    app = Starlette(routes=[Route("/anything", _ok)])
    app.add_middleware(BasicAuthMiddleware)
    return app


def _rate_limited_app(max_requests: int) -> Starlette:
    app = Starlette(routes=[
        Route("/chat", _ok, methods=["POST"]),
        Route("/other", _ok, methods=["GET"]),
    ])
    app.add_middleware(RateLimitMiddleware, max_requests=max_requests, window_seconds=3600)
    return app


def _basic_header(user: str, password: str) -> dict[str, str]:
    token = base64.b64encode(f"{user}:{password}".encode()).decode()
    return {"Authorization": f"Basic {token}"}


def test_basic_auth_noop_when_unset(monkeypatch):
    monkeypatch.delenv("DEMO_BASIC_AUTH_USER", raising=False)
    monkeypatch.delenv("DEMO_BASIC_AUTH_PASS", raising=False)
    c = TestClient(_basic_auth_app())
    r = c.get("/anything")
    assert r.status_code == 200


def test_basic_auth_rejects_missing_credentials(monkeypatch):
    monkeypatch.setenv("DEMO_BASIC_AUTH_USER", "demo")
    monkeypatch.setenv("DEMO_BASIC_AUTH_PASS", "secret")
    c = TestClient(_basic_auth_app())
    r = c.get("/anything")
    assert r.status_code == 401
    assert "WWW-Authenticate" in r.headers


def test_basic_auth_rejects_wrong_credentials(monkeypatch):
    monkeypatch.setenv("DEMO_BASIC_AUTH_USER", "demo")
    monkeypatch.setenv("DEMO_BASIC_AUTH_PASS", "secret")
    c = TestClient(_basic_auth_app())
    r = c.get("/anything", headers=_basic_header("demo", "wrong"))
    assert r.status_code == 401


def test_basic_auth_accepts_correct_credentials(monkeypatch):
    monkeypatch.setenv("DEMO_BASIC_AUTH_USER", "demo")
    monkeypatch.setenv("DEMO_BASIC_AUTH_PASS", "secret")
    c = TestClient(_basic_auth_app())
    r = c.get("/anything", headers=_basic_header("demo", "secret"))
    assert r.status_code == 200


def test_rate_limit_trips_after_cap():
    c = TestClient(_rate_limited_app(max_requests=3))
    for _ in range(3):
        assert c.post("/chat").status_code == 200
    r = c.post("/chat")
    assert r.status_code == 429


def test_rate_limit_only_applies_to_llm_routes():
    c = TestClient(_rate_limited_app(max_requests=1))
    assert c.post("/chat").status_code == 200
    assert c.post("/chat").status_code == 429
    # Unrelated route is never rate-limited, even after /chat trips.
    for _ in range(5):
        assert c.get("/other").status_code == 200
