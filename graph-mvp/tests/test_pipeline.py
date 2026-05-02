"""End-to-end smoke tests for the data + tool layers (no API needed)."""

from __future__ import annotations

import os
from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def synthetic_pipeline(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("graph-mvp-test")
    os.environ["GRAPH_DATA_DIR"] = str(tmp)
    os.environ["GRAPH_WIKI_DIR"] = str(tmp / "wiki")
    os.environ["GRAPH_DUCKDB_PATH"] = str(tmp / "staging.duckdb")
    os.environ["GRAPH_AUDIT_DB_PATH"] = str(tmp / "audit.sqlite")
    # Settings is lru_cached; clear so the env vars take effect.
    from src import config
    config.load_settings.cache_clear()
    settings = config.load_settings()

    from src.compile.compiler import compile_wiki
    from src.ingest.csv_loader import load_csvs
    from src.ingest.synthetic import generate

    generate(settings.raw_dir, seed=7)
    conn = load_csvs(settings.raw_dir, settings.duckdb_path)
    counts = compile_wiki(conn, settings.wiki_dir)
    return settings, counts


def test_synthetic_data_has_expected_shape(synthetic_pipeline):
    settings, _ = synthetic_pipeline
    assert (settings.raw_dir / "skus.csv").exists()
    assert (settings.raw_dir / "orders.csv").exists()


def test_wiki_compilation_produces_pages(synthetic_pipeline):
    _, counts = synthetic_pipeline
    assert counts["skus"] > 1000
    assert counts["suppliers"] == 20
    assert counts["customers"] == 500
    assert counts["concepts"] >= 3


def test_sql_tool_returns_rows(synthetic_pipeline):
    from src.tools.sql_query import run_sql
    rows = run_sql("SELECT category, COUNT(*) c FROM skus GROUP BY 1")
    assert {r["category"] for r in rows} >= {"Capacitor", "Motor", "Refrigerant"}


def test_wiki_search_finds_concept(synthetic_pipeline):
    from src.tools.wiki_read import read_wiki_page, search_wiki
    hits = search_wiki("R-410A", limit=5)
    assert any("r-410a-phase-out" in h["path"] for h in hits)
    body = read_wiki_page("concepts/r-410a-phase-out.md")
    assert "AIM Act" in body


def test_wiki_path_traversal_blocked(synthetic_pipeline):
    from src.tools.wiki_read import read_wiki_page
    with pytest.raises(ValueError):
        read_wiki_page("../../etc/passwd")


def test_audit_logger_roundtrip(synthetic_pipeline):
    from src.audit.logger import fetch_trace, log_step, new_trace_id
    tid = new_trace_id()
    log_step(tid, 1, "test_kind", {"foo": "bar"})
    log_step(tid, 2, "test_kind", {"foo": "baz"})
    trace = fetch_trace(tid)
    assert len(trace) == 2
    assert trace[0]["payload"] == {"foo": "bar"}


def test_api_404_on_missing_trace(synthetic_pipeline):
    from fastapi.testclient import TestClient
    from src.api.main import app
    client = TestClient(app)
    r = client.get("/audit/trace_nope")
    assert r.status_code == 404
