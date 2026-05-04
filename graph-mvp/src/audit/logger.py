"""Append-only trace logger backed by SQLite.

Every agent action - model call, tool call, tool result, final answer -
gets one row keyed by ``trace_id``. The chat UI reads these rows back
when the user clicks "show sources". Trust is the whole point.
"""

from __future__ import annotations

import json
import sqlite3
import uuid
from pathlib import Path
from typing import Any

from src.config import load_settings

_SCHEMA_FILE = Path(__file__).with_name("schema.sql")


def _connect() -> sqlite3.Connection:
    settings = load_settings()
    settings.audit_db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(settings.audit_db_path)
    conn.row_factory = sqlite3.Row
    conn.executescript(_SCHEMA_FILE.read_text(encoding="utf-8"))
    return conn


def new_trace_id() -> str:
    return f"trace_{uuid.uuid4().hex[:16]}"


def log_step(trace_id: str, iteration: int, kind: str, payload: dict[str, Any]) -> None:
    with _connect() as conn:
        conn.execute(
            "INSERT INTO trace_steps (trace_id, iteration, kind, payload_json) "
            "VALUES (?, ?, ?, ?)",
            (trace_id, iteration, kind, json.dumps(payload, default=str)),
        )


def fetch_trace(trace_id: str) -> list[dict[str, Any]]:
    with _connect() as conn:
        rows = conn.execute(
            "SELECT iteration, kind, payload_json, created_at FROM trace_steps "
            "WHERE trace_id = ? ORDER BY id",
            (trace_id,),
        ).fetchall()
    out: list[dict[str, Any]] = []
    for r in rows:
        out.append({
            "iteration": r["iteration"],
            "kind": r["kind"],
            "payload": json.loads(r["payload_json"]),
            "created_at": r["created_at"],
        })
    return out
