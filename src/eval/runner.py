"""Eval-run orchestration.

Two modes:

  - **retrieval-only** — call ``src.retrieval.search.retrieve()`` directly
    for each golden question. Measures recall@k + MRR. No agent, no
    ANTHROPIC_API_KEY needed. Fast and free; ideal for CI and for
    portfolio reviewers who don't have a key.

  - **agent** — run the full agent loop. Measures citation precision /
    recall in addition to retrieval. Needs a live ANTHROPIC_API_KEY.

Both modes write:
  - ``data/evals/{run_id}.jsonl`` — one row per question with retrieved /
    cited / latency / token usage.
  - ``data/evals/{run_id}.summary.json`` — aggregate ``MetricsSummary``.

The summary file is what Phase 7's Admin → Evals tab loads.
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

from src.config import load_settings  # noqa: F401 — triggers .env load
from src.eval.metrics import (
    MetricsSummary,
    PerQuestionScore,
    aggregate,
    score_question,
)
from src.retrieval.search import retrieve

load_settings()  # explicit nudge in case import elision skips the side effect

ROOT = Path(__file__).resolve().parents[2]
EVALS_DIR = Path(os.environ.get("GRAPH_DATA_DIR", ROOT / "data")) / "evals"


@dataclass(frozen=True)
class EvalQuestion:
    qid: str
    question: str
    expected_source_ids: list[str]
    expected_entities: list[str]
    notes: str | None = None


def read_golden(path: Path) -> list[EvalQuestion]:
    out: list[EvalQuestion] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("//"):
            continue
        rec = json.loads(line)
        out.append(EvalQuestion(
            qid=rec["qid"],
            question=rec["question"],
            expected_source_ids=list(rec.get("expected_source_ids", [])),
            expected_entities=list(rec.get("expected_entities", [])),
            notes=rec.get("notes"),
        ))
    return out


# ---------------------------------------------------------------------------
# Retrieval-only path
# ---------------------------------------------------------------------------


def _run_retrieval(q: EvalQuestion, k: int) -> tuple[PerQuestionScore, dict]:
    t0 = time.perf_counter()
    hits = retrieve(q.question, k=k, rerank=False)
    latency_ms = int((time.perf_counter() - t0) * 1000)
    retrieved = [h.source_id for h in hits]
    score = score_question(
        qid=q.qid,
        question=q.question,
        expected_source_ids=q.expected_source_ids,
        retrieved_source_ids=retrieved,
        cited_source_ids=None,
        latency_ms=latency_ms,
    )
    row = {
        "qid": q.qid,
        "question": q.question,
        "retrieved_source_ids": retrieved,
        "retrieved_chunk_ids": [h.chunk_id for h in hits],
        "retrieved_scores": [round(h.score, 4) for h in hits],
        "latency_ms": latency_ms,
        "mode": "retrieval-only",
    }
    return score, row


# ---------------------------------------------------------------------------
# Agent path (needs API key)
# ---------------------------------------------------------------------------


def _run_agent(q: EvalQuestion) -> tuple[PerQuestionScore, dict]:
    from src.agent.loop import run_agent
    t0 = time.perf_counter()
    try:
        resp = run_agent(q.question)
    except Exception as exc:
        return (
            score_question(
                qid=q.qid, question=q.question,
                expected_source_ids=q.expected_source_ids,
                retrieved_source_ids=[],
                cited_source_ids=[],
                error=f"{type(exc).__name__}: {exc}",
            ),
            {"qid": q.qid, "error": f"{type(exc).__name__}: {exc}", "mode": "agent"},
        )
    latency_ms = int((time.perf_counter() - t0) * 1000)

    # Pull retrieved + cited chunks from the trace.
    cited_source_ids = [c.source_id for c in resp.citations]
    retrieved_source_ids = _retrieved_from_trace(resp.trace_id)
    score = score_question(
        qid=q.qid,
        question=q.question,
        expected_source_ids=q.expected_source_ids,
        retrieved_source_ids=retrieved_source_ids,
        cited_source_ids=cited_source_ids,
        latency_ms=latency_ms,
    )
    row = {
        "qid": q.qid,
        "question": q.question,
        "trace_id": resp.trace_id,
        "iterations": resp.iterations,
        "answer": resp.answer,
        "retrieved_source_ids": retrieved_source_ids,
        "cited_source_ids": cited_source_ids,
        "citations": [asdict(c) for c in resp.citations],
        "latency_ms": latency_ms,
        "mode": "agent",
    }
    return score, row


def _retrieved_from_trace(trace_id: str) -> list[str]:
    """Pull source_ids from retrieve() tool calls in the audit log."""
    from src.audit.logger import fetch_trace
    out: list[str] = []
    for ev in fetch_trace(trace_id):
        if ev["kind"] != "tool_result":
            continue
        payload = ev.get("payload", {})
        if payload.get("name") != "retrieve":
            continue
        # tool_result preview text contains lines like "[c1] source-id-here"
        preview = payload.get("result_preview", "")
        import re
        for m in re.finditer(r"\[c\d+\]\s+(\S+)", preview):
            out.append(m.group(1))
    return out


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def run_eval(
    golden_path: Path,
    *,
    mode: str = "retrieval",
    k: int = 10,
    run_id: str | None = None,
    on_progress=None,
) -> tuple[Path, MetricsSummary]:
    """Run the agent over every question in the golden set.

    Returns (per-question JSONL path, aggregate ``MetricsSummary``).
    """
    if mode not in ("retrieval", "agent"):
        raise ValueError(f"unknown mode {mode!r} (use 'retrieval' or 'agent')")

    EVALS_DIR.mkdir(parents=True, exist_ok=True)
    run_id = run_id or _new_run_id(mode)
    jsonl_path = EVALS_DIR / f"{run_id}.jsonl"
    summary_path = EVALS_DIR / f"{run_id}.summary.json"

    questions = read_golden(golden_path)
    scores: list[PerQuestionScore] = []

    with jsonl_path.open("w", encoding="utf-8") as f:
        for q in questions:
            if mode == "retrieval":
                score, row = _run_retrieval(q, k=k)
            else:
                score, row = _run_agent(q)
            f.write(json.dumps(row) + "\n")
            f.flush()
            scores.append(score)
            if on_progress:
                on_progress(score)

    summary = aggregate(scores)
    summary_path.write_text(
        json.dumps({
            "run_id": run_id,
            "mode": mode,
            "k": k,
            "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            **{k: v for k, v in asdict(summary).items() if k != "by_qid"},
            "by_qid": asdict(summary)["by_qid"],
        }, indent=2),
        encoding="utf-8",
    )
    return jsonl_path, summary


def _new_run_id(mode: str) -> str:
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    return f"{ts}-{mode}"


def event_stream(
    golden_path: Path,
    *,
    mode: str = "retrieval",
    k: int = 10,
) -> Iterator[dict]:
    """Generator variant — yields a progress event per question + a final summary."""
    questions = read_golden(golden_path)
    scores: list[PerQuestionScore] = []
    yield {"kind": "started", "n_questions": len(questions), "mode": mode}
    for q in questions:
        if mode == "retrieval":
            score, _ = _run_retrieval(q, k=k)
        else:
            score, _ = _run_agent(q)
        scores.append(score)
        yield {"kind": "question", "qid": q.qid, "recall_at_5": score.recall_at_5,
               "reciprocal_rank": score.reciprocal_rank}
    yield {"kind": "summary", "summary": asdict(aggregate(scores))}
