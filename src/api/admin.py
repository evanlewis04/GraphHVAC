"""Admin endpoints — backs the UI's Ingest / Health / Evals tabs.

Three families:

  - ``/admin/sources``           — corpus browser: every manifest entry
                                   enriched with on-disk status, chunk
                                   count from LanceDB, and last-indexed
                                   timestamp from the audit log.
  - ``/admin/source/{source_id}`` — raw text for the "open source" button
                                   on citation cards.
  - ``/admin/health``            — runs the knowledge-health check on
                                   demand; returns the structured report.
  - ``/admin/evals``             — latest eval metrics + run history.
                                   Empty shape until Phase 8 generates
                                   real eval runs under ``data/evals/``.

All endpoints are read-only. No auth — local-only tool.
"""

from __future__ import annotations

import json
import os
import re
import sqlite3
from dataclasses import asdict
from pathlib import Path
from typing import Any

import lancedb
import yaml
from fastapi import APIRouter, HTTPException

from src.config import load_settings
from src.retrieval.index import DEFAULT_LANCEDB_PATH, TABLE_NAME
from src.retrieval.search import read_source as _read_source
from src.structure.health import run_health_check

router = APIRouter()

ROOT = Path(__file__).resolve().parents[2]
SOURCES_DIR = Path(os.environ.get("GRAPH_DATA_DIR", ROOT / "data")) / "sources"
MANIFEST_PATH = SOURCES_DIR / "manifest.yaml"
EVALS_DIR = Path(os.environ.get("GRAPH_DATA_DIR", ROOT / "data")) / "evals"


# ---------------------------------------------------------------------------
# Sources
# ---------------------------------------------------------------------------


def _chunk_counts_by_source() -> dict[str, int]:
    path = DEFAULT_LANCEDB_PATH
    if not path.exists():
        return {}
    db = lancedb.connect(str(path))
    if TABLE_NAME not in db.table_names():
        return {}
    rows = db.open_table(TABLE_NAME).to_arrow().to_pylist()
    counts: dict[str, int] = {}
    for r in rows:
        base = r["source_id"].split("#", 1)[0]
        counts[base] = counts.get(base, 0) + 1
    return counts


def _last_indexed_by_source() -> dict[str, str]:
    """Pull the most recent source_indexed timestamp per source from audit log."""
    settings = load_settings()
    if not settings.audit_db_path.exists():
        return {}
    conn = sqlite3.connect(settings.audit_db_path)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            "SELECT payload_json, created_at FROM trace_steps WHERE kind = 'source_indexed'"
        ).fetchall()
    finally:
        conn.close()
    out: dict[str, str] = {}
    for r in rows:
        try:
            payload = json.loads(r["payload_json"])
        except (TypeError, json.JSONDecodeError):
            continue
        sid = payload.get("source_id")
        if not sid:
            continue
        prev = out.get(sid)
        if prev is None or r["created_at"] > prev:
            out[sid] = r["created_at"]
    return out


@router.get("/admin/sources")
def list_sources() -> dict[str, Any]:
    if not MANIFEST_PATH.exists():
        raise HTTPException(404, "manifest.yaml not found; run scripts/generate_corpus.py")
    manifest = yaml.safe_load(MANIFEST_PATH.read_text(encoding="utf-8"))
    entries = manifest.get("sources", [])
    chunk_counts = _chunk_counts_by_source()
    last_indexed = _last_indexed_by_source()

    enriched: list[dict[str, Any]] = []
    for e in entries:
        sid = e["source_id"]
        path = SOURCES_DIR / e["path"]
        enriched.append({
            "source_id": sid,
            "title": e.get("title"),
            "type": e.get("type"),
            "bucket": e.get("bucket"),
            "issuer": e.get("issuer"),
            "manufacturer": e.get("manufacturer"),
            "refrigerants": e.get("refrigerants"),
            "regulations": e.get("regulations"),
            "doc_date": e.get("doc_date"),
            "license": e.get("license"),
            "path": e.get("path"),
            "on_disk": path.exists(),
            "size_bytes": path.stat().st_size if path.exists() else None,
            "chunk_count": chunk_counts.get(sid, 0),
            "last_indexed_at": last_indexed.get(sid),
        })

    # Roll up summary tiles for the UI header.
    summary = {
        "total_sources": len(enriched),
        "indexed_sources": sum(1 for e in enriched if e["chunk_count"] > 0),
        "total_chunks": sum(e["chunk_count"] for e in enriched),
        "by_bucket": _counts(enriched, "bucket"),
        "by_license": _counts(enriched, "license"),
    }
    return {"summary": summary, "sources": enriched}


def _counts(items: list[dict[str, Any]], key: str) -> dict[str, int]:
    out: dict[str, int] = {}
    for it in items:
        v = it.get(key) or "—"
        out[str(v)] = out.get(str(v), 0) + 1
    return out


@router.get("/admin/source/{source_id:path}")
def get_source_raw(source_id: str, max_chars: int = 32000) -> dict[str, Any]:
    """Return raw text for a source document. Backs the "Open source" button."""
    text = _read_source(source_id, max_chars=max_chars)
    return {"source_id": source_id, "content": text}


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------


@router.get("/admin/health")
def get_health(use_llm: bool = False) -> dict[str, Any]:
    """Run the structure-health check live and return the structured report.

    ``use_llm=true`` includes Sonnet contradiction detection (slow + costs).
    """
    report = run_health_check(use_llm=use_llm, write_report=True)
    return asdict(report)


# ---------------------------------------------------------------------------
# Evals (Phase 8 will populate)
# ---------------------------------------------------------------------------


_RUN_ID_RE = re.compile(r"^[A-Za-z0-9_\-]+$")


@router.get("/admin/evals")
def list_evals() -> dict[str, Any]:
    """Return latest eval summary + a list of past runs.

    Empty shape when ``data/evals/`` doesn't exist yet — the UI shows a
    "no runs" hint pointing at ``scripts/run_evals.py``.
    """
    if not EVALS_DIR.exists():
        return {"runs": [], "latest": None}
    summaries = sorted(EVALS_DIR.glob("*.summary.json"))
    runs: list[dict[str, Any]] = []
    for summary_path in summaries:
        try:
            data = json.loads(summary_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        runs.append({
            "run_id": summary_path.stem.removesuffix(".summary"),
            "summary_path": str(summary_path.relative_to(EVALS_DIR)),
            "metrics": data,
            "mtime": summary_path.stat().st_mtime,
        })
    runs.sort(key=lambda r: r["mtime"], reverse=True)
    latest = runs[0] if runs else None
    return {"runs": runs, "latest": latest}


@router.get("/admin/evals/{run_id}")
def get_eval_run(run_id: str) -> dict[str, Any]:
    if not _RUN_ID_RE.match(run_id):
        raise HTTPException(400, "invalid run_id")
    summary_path = EVALS_DIR / f"{run_id}.summary.json"
    detail_path = EVALS_DIR / f"{run_id}.jsonl"
    if not summary_path.exists():
        raise HTTPException(404, f"no eval run {run_id!r}")
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    details: list[dict[str, Any]] = []
    if detail_path.exists():
        for line in detail_path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                try:
                    details.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return {"run_id": run_id, "summary": summary, "details": details}
