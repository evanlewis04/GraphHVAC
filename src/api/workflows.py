"""Workflow endpoints.

  - GET  /workflows               — list workflow metadata (slug, title,
                                    description, parameter schemas) for
                                    the UI's workflow picker.
  - POST /workflows/{slug}/run    — synchronous; returns the final
                                    AgentResponse JSON (answer +
                                    citations + trace_id + iterations).
  - POST /workflows/{slug}/stream — SSE; emits the same event stream as
                                    /chat/stream, prefixed with a
                                    ``workflow_started`` event.
"""

from __future__ import annotations

import json
from dataclasses import asdict
from typing import Any, Iterator

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from src.config import load_settings
from src.workflows import WORKFLOWS, run_workflow, stream_workflow
from src.workflows.runner import WorkflowError, _resolve, build_prompt

router = APIRouter()


class WorkflowRunRequest(BaseModel):
    params: dict[str, Any] = {}


class WorkflowRunResponse(BaseModel):
    answer: str
    trace_id: str
    iterations: int
    citations: list[dict[str, Any]] = []
    prompt: str


@router.get("/workflows")
def list_workflows() -> list[dict[str, Any]]:
    return [w.to_dict() for w in WORKFLOWS]


@router.post("/workflows/{slug}/run", response_model=WorkflowRunResponse)
def run(slug: str, req: WorkflowRunRequest) -> WorkflowRunResponse:
    try:
        workflow = _resolve(slug)
        prompt = build_prompt(workflow, req.params)
    except WorkflowError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    try:
        result = run_workflow(slug, req.params)
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return WorkflowRunResponse(
        answer=result.answer,
        trace_id=result.trace_id,
        iterations=result.iterations,
        citations=[asdict(c) for c in result.citations],
        prompt=prompt,
    )


def _sse(event: dict) -> str:
    return f"data: {json.dumps(event, default=str)}\n\n"


@router.post("/workflows/{slug}/stream")
def run_stream(slug: str, req: WorkflowRunRequest):
    # Fail-fast input + config errors so the browser gets a clean HTTP code.
    try:
        workflow = _resolve(slug)
        build_prompt(workflow, req.params)  # validates; result re-built in stream
    except WorkflowError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if not load_settings().anthropic_api_key:
        raise HTTPException(
            status_code=500,
            detail="ANTHROPIC_API_KEY is not set; workflow cannot run.",
        )

    def generator() -> Iterator[str]:
        try:
            for event in stream_workflow(slug, req.params):
                yield _sse(event)
        except Exception as exc:
            yield _sse({"kind": "error", "message": f"{type(exc).__name__}: {exc}"})

    return StreamingResponse(
        generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )
