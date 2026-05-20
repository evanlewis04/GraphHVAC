"""Chat endpoints.

- POST /chat        : synchronous; returns the final AgentResponse JSON
- POST /chat/stream : SSE; emits incremental events as the loop runs
"""

from __future__ import annotations

import json
from dataclasses import asdict
from typing import Any, Iterator

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from src.agent.loop import run_agent, stream_agent
from src.config import load_settings

router = APIRouter()


class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    answer: str
    trace_id: str
    iterations: int
    citations: list[dict[str, Any]] = []


@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    """Synchronous chat. Kept for scripted callers and as a fallback."""
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="Question must be non-empty.")
    try:
        result = run_agent(req.question)
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return ChatResponse(
        answer=result.answer,
        trace_id=result.trace_id,
        iterations=result.iterations,
        citations=[asdict(c) for c in result.citations],
    )


def _sse(event: dict) -> str:
    """Format a dict as a single SSE message."""
    return f"data: {json.dumps(event, default=str)}\n\n"


@router.post("/chat/stream")
def chat_stream(req: ChatRequest):
    """Server-sent events. The body is iterated lazily so the browser sees
    progress as soon as each event is produced.

    Fail fast on input/config errors so the browser gets a clean HTTP
    error code instead of an empty stream."""
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="Question must be non-empty.")
    if not load_settings().anthropic_api_key:
        raise HTTPException(status_code=500, detail="ANTHROPIC_API_KEY is not set; agent cannot run.")

    def generator() -> Iterator[str]:
        try:
            for event in stream_agent(req.question):
                yield _sse(event)
        except Exception as exc:  # never let the stream die silently
            yield _sse({"kind": "error", "message": f"{type(exc).__name__}: {exc}"})

    return StreamingResponse(
        generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "X-Accel-Buffering": "no",  # disables nginx buffering when proxied
            "Connection": "keep-alive",
        },
    )
