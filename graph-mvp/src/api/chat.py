"""POST /chat - invoke the agent loop and return the answer + trace_id."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.agent.loop import run_agent

router = APIRouter()


class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    answer: str
    trace_id: str
    iterations: int


@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="Question must be non-empty.")
    try:
        result = run_agent(req.question)
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return ChatResponse(answer=result.answer, trace_id=result.trace_id, iterations=result.iterations)
