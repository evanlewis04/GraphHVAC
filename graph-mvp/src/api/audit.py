"""GET /audit/{trace_id} — return the full agent trace for the
"show sources" panel in the UI."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter

router = APIRouter()


@router.get("/audit/{trace_id}")
def get_trace(trace_id: str) -> list[dict[str, Any]]:
    raise NotImplementedError
