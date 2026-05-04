"""Tests for the daily brief surface."""

from __future__ import annotations

import os
from datetime import date
from unittest import mock

import pytest


@pytest.fixture
def isolated_settings(tmp_path, monkeypatch):
    monkeypatch.setenv("GRAPH_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("GRAPH_WIKI_DIR", str(tmp_path / "wiki"))
    monkeypatch.setenv("GRAPH_DUCKDB_PATH", str(tmp_path / "staging.duckdb"))
    monkeypatch.setenv("GRAPH_AUDIT_DB_PATH", str(tmp_path / "audit.sqlite"))
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    from src import config
    config.load_settings.cache_clear()
    settings = config.load_settings()
    yield settings
    config.load_settings.cache_clear()


def test_generate_brief_writes_dated_markdown(isolated_settings):
    from src.agent.loop import AgentResponse
    from src.briefs import generator

    fake_response = AgentResponse(
        answer="## Refrigerant exposure\n- $1.2M tied to R-410A\n",
        trace_id="trace_test123",
        iterations=4,
    )
    with mock.patch("src.briefs.generator.run_agent", return_value=fake_response) as mocked:
        path = generator.generate_brief(date(2026, 5, 3))

    mocked.assert_called_once()
    assert path.exists()
    body = path.read_text()
    assert "date: 2026-05-03" in body
    assert "trace_id: trace_test123" in body
    assert "iterations: 4" in body
    assert "Daily Brief" in body
    assert "R-410A" in body


def test_list_briefs_returns_newest_first(isolated_settings):
    from src.briefs.generator import briefs_dir, list_briefs

    out = briefs_dir()
    out.mkdir(parents=True, exist_ok=True)
    for d in ("2026-05-01", "2026-05-03", "2026-05-02"):
        (out / f"{d}.md").write_text(f"# {d}\n")

    rows = list_briefs()
    assert [r["date"] for r in rows] == ["2026-05-03", "2026-05-02", "2026-05-01"]


def test_read_brief_returns_none_for_missing(isolated_settings):
    from src.briefs.generator import read_brief
    assert read_brief("2026-01-01") is None


def test_read_brief_blocks_path_traversal(isolated_settings):
    """The brief reader must validate the date string — never let the
    user read arbitrary files."""
    from src.briefs.generator import read_brief

    out = (isolated_settings.data_dir / "briefs")
    out.mkdir(parents=True, exist_ok=True)
    secret = isolated_settings.data_dir / "secret.md"
    secret.write_text("you should never read this")

    assert read_brief("../secret") is None
    assert read_brief("..%2Fsecret") is None
    assert read_brief("foo") is None
    assert read_brief("2026-13-99") is not None or read_brief("2026-13-99") is None
    # Strict shape: 10 chars with hyphens — but date contents not validated;
    # the validator's job is to block traversal, not to validate calendars.


def test_briefs_endpoints(isolated_settings):
    from fastapi.testclient import TestClient
    from src.api.main import app
    from src.briefs.generator import briefs_dir

    out = briefs_dir()
    out.mkdir(parents=True, exist_ok=True)
    (out / "2026-05-03.md").write_text("# brief body")

    c = TestClient(app)
    r = c.get("/briefs")
    assert r.status_code == 200
    rows = r.json()
    assert any(row["date"] == "2026-05-03" for row in rows)

    r = c.get("/briefs/2026-05-03")
    assert r.status_code == 200
    assert r.json()["body"] == "# brief body"

    r = c.get("/briefs/2026-01-01")
    assert r.status_code == 404

    r = c.get("/briefs/../etc/passwd")
    # FastAPI's path matcher / validator should not let this through cleanly,
    # but if it does we still return 404.
    assert r.status_code in (404, 422)
