"""Append-only trace logger backed by SQLite.

Every agent action — model call, tool call, tool result, final answer —
gets one row keyed by ``trace_id``. The chat UI reads these rows back
when the user clicks "show sources". Trust is the whole point.
"""

from __future__ import annotations

from typing import Any


def new_trace_id() -> str:
    raise NotImplementedError


def log_step(trace_id: str, iteration: int, kind: str, payload: dict[str, Any]) -> None:
    raise NotImplementedError


def fetch_trace(trace_id: str) -> list[dict[str, Any]]:
    raise NotImplementedError
