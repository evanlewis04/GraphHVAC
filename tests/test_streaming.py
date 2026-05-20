"""Tests for the streaming agent path: stream_agent generator + SSE endpoint.

Uses a fake Anthropic client to exercise the full event sequence without
network access or API key.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path

import pytest


@dataclass
class _Block:
    type: str
    text: str = ""
    id: str = ""
    name: str = ""
    input: dict = field(default_factory=dict)


@dataclass
class _Usage:
    input_tokens: int = 100
    output_tokens: int = 50
    cache_read_input_tokens: int = 0
    cache_creation_input_tokens: int = 0


@dataclass
class _Response:
    stop_reason: str
    content: list
    usage: _Usage = field(default_factory=_Usage)


class FakeMessages:
    def __init__(self, scripted: list[_Response]) -> None:
        self._scripted = list(scripted)
        self.calls: list[dict] = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        if not self._scripted:
            raise AssertionError("FakeMessages ran out of scripted responses")
        return self._scripted.pop(0)


class FakeClient:
    def __init__(self, scripted: list[_Response]) -> None:
        self.messages = FakeMessages(scripted)


@pytest.fixture(scope="module")
def pipeline(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("graph-stream")
    os.environ["GRAPH_DATA_DIR"] = str(tmp)
    os.environ["GRAPH_WIKI_DIR"] = str(tmp / "wiki")
    os.environ["GRAPH_DUCKDB_PATH"] = str(tmp / "staging.duckdb")
    os.environ["GRAPH_AUDIT_DB_PATH"] = str(tmp / "audit.sqlite")
    os.environ["ANTHROPIC_API_KEY"] = "test-key"
    from src import config
    config.load_settings.cache_clear()
    settings = config.load_settings()

    from src.compile.compiler import compile_wiki
    from src.ingest.csv_loader import load_csvs
    from src.ingest.synthetic import generate

    generate(settings.raw_dir, seed=4)
    conn = load_csvs(settings.raw_dir, settings.duckdb_path)
    compile_wiki(conn, settings.wiki_dir)
    yield settings
    os.environ.pop("ANTHROPIC_API_KEY", None)
    config.load_settings.cache_clear()


def _patch_client(monkeypatch, scripted: list[_Response]) -> FakeClient:
    fake = FakeClient(scripted)
    from src.agent import loop as loop_mod
    monkeypatch.setattr(loop_mod.anthropic, "Anthropic", lambda **kw: fake)
    return fake


# ---- stream_agent generator ----

def test_stream_emits_started_then_final_for_simple_answer(pipeline, monkeypatch):
    from src.agent.loop import stream_agent
    _patch_client(monkeypatch, [
        _Response(stop_reason="end_turn",
                  content=[_Block(type="text", text="The answer is 42.")]),
    ])
    events = list(stream_agent("what's the meaning of life?"))
    kinds = [e["kind"] for e in events]
    assert kinds[0] == "started"
    assert "iteration" in kinds
    assert kinds[-1] == "final"
    final = events[-1]
    assert final["answer"] == "The answer is 42."
    assert final["iterations"] == 1
    assert final["trace_id"]


def test_stream_emits_tool_call_events(pipeline, monkeypatch):
    """Multi-step trace: model asks for a tool, then returns end_turn."""
    from src.agent.loop import stream_agent
    _patch_client(monkeypatch, [
        _Response(stop_reason="tool_use", content=[
            _Block(type="tool_use", id="tu_1", name="run_sql",
                   input={"query": "SELECT COUNT(*) FROM skus"}),
        ]),
        _Response(stop_reason="end_turn",
                  content=[_Block(type="text", text="There are 4998 SKUs.")]),
    ])
    events = list(stream_agent("how many SKUs?"))
    kinds = [e["kind"] for e in events]
    assert kinds.count("tool_call") == 1
    assert kinds.count("iteration") == 2  # one per loop pass
    tc = next(e for e in events if e["kind"] == "tool_call")
    assert tc["name"] == "run_sql"
    assert "SELECT COUNT(*) FROM skus" in tc["input"]["query"]
    assert events[-1]["kind"] == "final"
    assert "4998" in events[-1]["answer"]


def test_stream_yields_error_when_no_api_key(pipeline, monkeypatch):
    from src.agent.loop import stream_agent
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    from src import config
    config.load_settings.cache_clear()
    events = list(stream_agent("hi"))
    assert len(events) == 1
    assert events[0] == {"kind": "error", "message": "ANTHROPIC_API_KEY is not set; agent cannot run."}
    # restore
    os.environ["ANTHROPIC_API_KEY"] = "test-key"
    config.load_settings.cache_clear()


def test_stream_max_iterations_emits_final(pipeline, monkeypatch):
    """Generator must terminate cleanly even when the model never returns end_turn."""
    from src.agent.loop import stream_agent

    # Always ask for a tool — never end_turn
    looper = _Response(stop_reason="tool_use", content=[
        _Block(type="tool_use", id="tu_x", name="search_wiki", input={"query": "x"}),
    ])
    _patch_client(monkeypatch, [looper, looper, looper])
    events = list(stream_agent("loop forever", max_iterations=3))
    final = next(e for e in events if e["kind"] == "final")
    assert final["iterations"] == 3
    assert "wasn't able to complete" in final["answer"]


def test_run_agent_wrapper_returns_same_final(pipeline, monkeypatch):
    """The synchronous wrapper should produce the same final answer as the stream."""
    from src.agent.loop import run_agent
    _patch_client(monkeypatch, [
        _Response(stop_reason="end_turn",
                  content=[_Block(type="text", text="Sync result.")]),
    ])
    result = run_agent("ping")
    assert result.answer == "Sync result."
    assert result.iterations == 1


# ---- SSE endpoint ----

def test_chat_stream_400_on_empty(pipeline, monkeypatch):
    from fastapi.testclient import TestClient
    from src.api.main import app
    c = TestClient(app)
    r = c.post("/chat/stream", json={"question": "  "})
    assert r.status_code == 400


def test_chat_stream_500_when_no_api_key(pipeline, monkeypatch):
    """Fail fast with HTTP 500 before opening the stream — the frontend
    can show a clean error rather than an empty SSE."""
    from fastapi.testclient import TestClient
    from src.api.main import app
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    from src import config
    config.load_settings.cache_clear()
    c = TestClient(app)
    r = c.post("/chat/stream", json={"question": "hi"})
    assert r.status_code == 500
    os.environ["ANTHROPIC_API_KEY"] = "test-key"
    config.load_settings.cache_clear()


def test_chat_stream_emits_sse_events(pipeline, monkeypatch):
    from fastapi.testclient import TestClient
    from src.api.main import app
    _patch_client(monkeypatch, [
        _Response(stop_reason="tool_use", content=[
            _Block(type="tool_use", id="tu_1", name="search_wiki", input={"query": "R-410A"}),
        ]),
        _Response(stop_reason="end_turn",
                  content=[_Block(type="text", text="See the R-410A concept page.")]),
    ])
    c = TestClient(app)
    with c.stream("POST", "/chat/stream", json={"question": "tell me about R-410A"}) as r:
        assert r.status_code == 200
        assert r.headers["content-type"].startswith("text/event-stream")
        body = "".join(r.iter_text())

    payloads = []
    for chunk in body.split("\n\n"):
        for line in chunk.split("\n"):
            if line.startswith("data:"):
                payloads.append(json.loads(line[5:].strip()))

    kinds = [p["kind"] for p in payloads]
    assert "started" in kinds
    assert "tool_call" in kinds
    assert "final" in kinds
    final = next(p for p in payloads if p["kind"] == "final")
    assert "R-410A" in final["answer"]
    assert final["trace_id"]


def test_chat_stream_writes_complete_audit_trail(pipeline, monkeypatch):
    """Even when streamed, the audit log must contain the full trace
    (the trust story depends on this)."""
    from fastapi.testclient import TestClient
    from src.api.main import app
    from src.audit.logger import fetch_trace

    _patch_client(monkeypatch, [
        _Response(stop_reason="tool_use", content=[
            _Block(type="tool_use", id="tu_a", name="run_sql",
                   input={"query": "SELECT 1"}),
        ]),
        _Response(stop_reason="end_turn",
                  content=[_Block(type="text", text="Done.")]),
    ])
    c = TestClient(app)
    with c.stream("POST", "/chat/stream", json={"question": "x"}) as r:
        body = "".join(r.iter_text())
    final = next(
        json.loads(line[5:].strip())
        for chunk in body.split("\n\n") for line in chunk.split("\n")
        if line.startswith("data:") and json.loads(line[5:].strip())["kind"] == "final"
    )
    trace = fetch_trace(final["trace_id"])
    kinds = [s["kind"] for s in trace]
    assert "user_question" in kinds
    assert "tool_call" in kinds
    assert "tool_result" in kinds
    assert "model_response" in kinds
