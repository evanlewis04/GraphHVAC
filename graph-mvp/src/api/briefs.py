"""Brief endpoints.

- GET /briefs           : list all briefs (newest first)
- GET /briefs/{date}    : full markdown body for one date
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from src.briefs.generator import list_briefs, read_brief

router = APIRouter()


@router.get("/briefs")
def get_briefs() -> list[dict]:
    return list_briefs()


@router.get("/briefs/{date_str}")
def get_brief(date_str: str) -> dict:
    body = read_brief(date_str)
    if body is None:
        raise HTTPException(status_code=404, detail=f"No brief for {date_str}")
    return {"date": date_str, "body": body}
