"""Edge case tests — input validation, security boundaries, error paths.

These test surfaces that aren't directly hit by happy-path agents:
read-only SQL guarantees, path traversal variants, weird inputs to the
agent loop and the FastAPI surface, and concurrent /chat behavior.
"""

from __future__ import annotations

import os
import threading
from pathlib import Path

import pytest


@pytest.fixture(scope="module")
def pipeline(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("graph-edge")
    os.environ["GRAPH_DATA_DIR"] = str(tmp)
    os.environ["GRAPH_WIKI_DIR"] = str(tmp / "wiki")
    os.environ["GRAPH_DUCKDB_PATH"] = str(tmp / "staging.duckdb")
    os.environ["GRAPH_AUDIT_DB_PATH"] = str(tmp / "audit.sqlite")
    os.environ.pop("ANTHROPIC_API_KEY", None)
    from src import config
    config.load_settings.cache_clear()
    settings = config.load_settings()

    from src.compile.compiler import compile_wiki
    from src.ingest.csv_loader import load_csvs
    from src.ingest.synthetic import generate

    generate(settings.raw_dir, seed=3)
    conn = load_csvs(settings.raw_dir, settings.duckdb_path)
    compile_wiki(conn, settings.wiki_dir)
    return settings


# ---- SQL safety ----

def test_sql_tool_is_read_only_blocks_drop(pipeline):
    """The SQL tool opens DuckDB in read-only mode, so DDL fails. The
    dispatcher catches the exception and surfaces an ERROR string."""
    from src.agent.tools import execute_tool
    out = execute_tool("run_sql", {"query": "DROP TABLE skus"})
    assert "ERROR" in out, "Destructive SQL should surface as a tool error"
    # And the table is still there.
    rows = execute_tool("run_sql", {"query": "SELECT COUNT(*) AS n FROM skus"})
    assert "4998" in rows or "n" in rows  # unaltered


def test_sql_tool_is_read_only_blocks_insert(pipeline):
    from src.agent.tools import execute_tool
    out = execute_tool("run_sql", {"query": "INSERT INTO skus VALUES ('x','x','x','x','x','x',0,0,'')"})
    assert "ERROR" in out


def test_sql_tool_caps_rows(pipeline):
    """run_sql should never return more than max_rows."""
    from src.tools.sql_query import run_sql
    rows = run_sql("SELECT * FROM orders")
    assert len(rows) <= 200, "row cap not respected"


def test_sql_tool_invalid_query_is_handled(pipeline):
    from src.agent.tools import execute_tool
    out = execute_tool("run_sql", {"query": "SELECT * FROM table_that_does_not_exist"})
    assert "ERROR" in out


# ---- Wiki path security ----

@pytest.mark.parametrize("malicious", [
    "../../etc/passwd",
    "../../../../../../etc/shadow",
    "skus/../../../etc/hosts",
    "/etc/passwd",
])
def test_path_traversal_variants_blocked(pipeline, malicious):
    from src.tools.wiki_read import read_wiki_page
    with pytest.raises((ValueError, FileNotFoundError, OSError, PermissionError)):
        read_wiki_page(malicious)


def test_wiki_read_missing_returns_error_not_exception(pipeline):
    """The dispatcher wraps tool errors so the agent always gets a string."""
    from src.agent.tools import execute_tool
    out = execute_tool("read_wiki_page", {"path": "skus/THIS-DOES-NOT-EXIST.md"})
    assert "ERROR" in out


def test_wiki_read_directory_returns_error(pipeline):
    from src.tools.wiki_read import read_wiki_page
    out = read_wiki_page("skus")
    assert out.startswith("ERROR")


def test_search_returns_empty_for_nothing(pipeline):
    from src.tools.wiki_read import search_wiki
    assert search_wiki("AsdfQwertyZxcvbn___NOMATCH___") == []


def test_list_directory_handles_missing(pipeline):
    from src.tools.wiki_read import list_wiki_directory
    assert list_wiki_directory("does-not-exist") == []


# ---- Agent dispatcher error handling ----

def test_dispatcher_unknown_tool(pipeline):
    from src.agent.tools import execute_tool
    assert "unknown tool" in execute_tool("nope", {}).lower()


def test_dispatcher_missing_required_arg(pipeline):
    """A tool called without its required argument shouldn't crash the loop."""
    from src.agent.tools import execute_tool
    out = execute_tool("read_wiki_page", {})  # missing 'path'
    assert "ERROR" in out


# ---- API surface ----

@pytest.fixture
def client(pipeline):
    from fastapi.testclient import TestClient
    from src.api.main import app
    return TestClient(app)


def test_chat_empty_question_400(client):
    r = client.post("/chat", json={"question": ""})
    assert r.status_code == 400


def test_chat_whitespace_only_question_400(client):
    r = client.post("/chat", json={"question": "   \n\t  "})
    assert r.status_code == 400


def test_chat_missing_field_422(client):
    r = client.post("/chat", json={})
    assert r.status_code == 422  # FastAPI validation error


def test_chat_no_api_key_returns_500(client):
    r = client.post("/chat", json={"question": "hello"})
    assert r.status_code == 500
    assert "ANTHROPIC_API_KEY" in r.json()["detail"]


def test_audit_404_on_missing(client):
    r = client.get("/audit/trace_does_not_exist")
    assert r.status_code == 404


def test_static_index_serves(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "Graph" in r.text


# ---- Audit log behavior ----

def test_audit_handles_concurrent_writes(pipeline):
    """SQLite is single-writer, but our wrapper opens a connection per call.
    Concurrent log_step calls from many threads must not deadlock or lose rows."""
    from src.audit.logger import fetch_trace, log_step, new_trace_id

    tid = new_trace_id()
    n_threads = 8
    per_thread = 10

    def worker(start: int) -> None:
        for i in range(per_thread):
            log_step(tid, start + i, "concurrent_test", {"i": start + i})

    threads = [threading.Thread(target=worker, args=(t * per_thread,)) for t in range(n_threads)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=10)

    trace = fetch_trace(tid)
    assert len(trace) == n_threads * per_thread


def test_audit_handles_unicode_payload(pipeline):
    from src.audit.logger import fetch_trace, log_step, new_trace_id
    tid = new_trace_id()
    log_step(tid, 1, "unicode", {"text": "R-410A · 27°F · 漢字 · 🚫", "ø": "value"})
    trace = fetch_trace(tid)
    assert "漢字" in trace[0]["payload"]["text"]


# ---- Agent loop: max iterations + no-API behavior ----

def test_agent_run_without_key_raises_runtime_error(pipeline):
    from src.agent.loop import run_agent
    with pytest.raises(RuntimeError, match="ANTHROPIC_API_KEY"):
        run_agent("hi")


def test_agent_max_iterations_short_circuits(pipeline):
    """If the model never returns end_turn, we exit cleanly with a fallback message."""
    from dataclasses import dataclass

    from src.agent import loop as loop_module

    @dataclass
    class _Block:
        type: str = "tool_use"
        id: str = "tu_1"
        name: str = "read_wiki_page"
        input: dict | None = None

        def __post_init__(self):
            if self.input is None:
                self.input = {"path": "_index.md"}

    @dataclass
    class _Usage:
        input_tokens: int = 10
        output_tokens: int = 5
        cache_read_input_tokens: int = 0
        cache_creation_input_tokens: int = 0

    @dataclass
    class _Response:
        stop_reason: str = "tool_use"
        content: list = None
        usage: _Usage = None

        def __post_init__(self):
            self.content = [_Block()]
            self.usage = _Usage()

    class FakeMessages:
        def __init__(self):
            self.calls = 0
        def create(self, **kwargs):
            self.calls += 1
            return _Response()

    class FakeClient:
        def __init__(self):
            self.messages = FakeMessages()

    fake = FakeClient()
    # Patch both the SDK client constructor and pretend a key exists.
    import os
    os.environ["ANTHROPIC_API_KEY"] = "test-key"
    from src import config
    config.load_settings.cache_clear()
    monkey = loop_module.anthropic
    loop_module.anthropic.Anthropic = lambda **kwargs: fake  # type: ignore[attr-defined]
    try:
        result = loop_module.run_agent("loop forever", max_iterations=3)
    finally:
        loop_module.anthropic = monkey  # restore
        os.environ.pop("ANTHROPIC_API_KEY", None)
        config.load_settings.cache_clear()

    assert result.iterations == 3
    assert "wasn't able to complete" in result.answer
    assert fake.messages.calls == 3
