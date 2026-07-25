"""Brief endpoints.

- GET  /briefs           : list all briefs (newest first)
- GET  /briefs/{date}    : full markdown body for one date
- POST /briefs/generate  : generate today's brief and return its body
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from src.briefs.generator import generate_brief, list_briefs, read_brief

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


@router.post("/briefs/generate")
def post_generate_brief() -> dict:
    try:
        path = generate_brief()
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    date_str = path.stem
    return {"date": date_str, "body": path.read_text(encoding="utf-8")}
