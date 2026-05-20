"""GET /audit/{trace_id} - return the full agent trace for the
"show sources" panel in the UI."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException

from src.audit.logger import fetch_trace

router = APIRouter()


@router.get("/audit/{trace_id}")
def get_trace(trace_id: str) -> list[dict[str, Any]]:
    rows = fetch_trace(trace_id)
    if not rows:
        raise HTTPException(status_code=404, detail=f"Unknown trace_id: {trace_id}")
    return rows
