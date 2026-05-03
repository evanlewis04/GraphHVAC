"""The core agent loop - Claude with tool use, hand-rolled in ~200 lines.

No agent framework on purpose. The loop calls Claude, executes any
requested tools, appends the result to the conversation, and stops on
``end_turn`` or when ``max_iterations`` is hit. Every step writes to
the audit log.

Two entry points:
- ``run_agent`` returns a final ``AgentResponse`` synchronously
- ``stream_agent`` yields a sequence of small JSON-serializable events
  (started / iteration / tool_call / final / error) so the FastAPI SSE
  endpoint can render progress in real time. Both paths share the same
  underlying machinery, so the audit log is identical.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterator

import anthropic

from src.agent.prompts import AGENT_SYSTEM_PROMPT
from src.agent.router import pick_model
from src.agent.tools import AGENT_TOOLS, execute_tool
from src.audit.logger import log_step, new_trace_id
from src.config import load_settings


@dataclass
class AgentResponse:
    answer: str
    trace_id: str
    iterations: int


def _serialize_block(block) -> dict:
    """Reduce a content block to a JSON-serializable dict for the audit log."""
    if block.type == "text":
        return {"type": "text", "text": block.text}
    if block.type == "tool_use":
        return {"type": "tool_use", "id": block.id, "name": block.name, "input": block.input}
    if block.type == "thinking":
        return {"type": "thinking", "thinking": getattr(block, "thinking", "")}
    return {"type": block.type}


def _final_text(response) -> str:
    parts = [b.text for b in response.content if b.type == "text"]
    return "\n".join(p for p in parts if p).strip()


def _make_client() -> anthropic.Anthropic:
    settings = load_settings()
    if not settings.anthropic_api_key:
        raise RuntimeError("ANTHROPIC_API_KEY is not set; agent cannot run.")
    return anthropic.Anthropic(api_key=settings.anthropic_api_key)


def stream_agent(
    user_question: str,
    trace_id: str | None = None,
    max_iterations: int = 15,
) -> Iterator[dict[str, Any]]:
    """Run the agent loop and yield a stream of events.

    Event kinds:
      - ``started``   : { trace_id, model }
      - ``iteration`` : { iteration }
      - ``tool_call`` : { iteration, name, input }
      - ``final``     : { answer, trace_id, iterations }
      - ``error``     : { message }

    All audit-log writes happen here, identical to the non-streaming path.
    """
    try:
        client = _make_client()
    except RuntimeError as exc:
        yield {"kind": "error", "message": str(exc)}
        return

    trace = trace_id or new_trace_id()
    model = pick_model(user_question)

    log_step(trace, 0, "user_question", {"question": user_question, "model": model})
    yield {"kind": "started", "trace_id": trace, "model": model}

    messages: list[dict] = [{"role": "user", "content": user_question}]

    for iteration in range(1, max_iterations + 1):
        yield {"kind": "iteration", "iteration": iteration}

        try:
            response = client.messages.create(
                model=model,
                max_tokens=4096,
                system=[
                    {
                        "type": "text",
                        "text": AGENT_SYSTEM_PROMPT,
                        "cache_control": {"type": "ephemeral"},
                    }
                ],
                tools=AGENT_TOOLS,
                messages=messages,
            )
        except anthropic.APIError as exc:
            log_step(trace, iteration, "api_error", {"error": str(exc)})
            yield {"kind": "error", "message": f"Claude API error: {exc}"}
            return

        log_step(trace, iteration, "model_response", {
            "stop_reason": response.stop_reason,
            "content": [_serialize_block(b) for b in response.content],
            "usage": {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
                "cache_read_input_tokens": getattr(response.usage, "cache_read_input_tokens", 0),
                "cache_creation_input_tokens": getattr(
                    response.usage, "cache_creation_input_tokens", 0
                ),
            },
        })

        if response.stop_reason == "end_turn":
            yield {
                "kind": "final",
                "answer": _final_text(response),
                "trace_id": trace,
                "iterations": iteration,
            }
            return

        if response.stop_reason != "tool_use":
            yield {
                "kind": "final",
                "answer": f"[stop_reason={response.stop_reason}] " + _final_text(response),
                "trace_id": trace,
                "iterations": iteration,
            }
            return

        messages.append({"role": "assistant", "content": response.content})

        tool_results = []
        for block in response.content:
            if block.type != "tool_use":
                continue
            log_step(trace, iteration, "tool_call", {
                "id": block.id, "name": block.name, "input": block.input,
            })
            yield {
                "kind": "tool_call",
                "iteration": iteration,
                "name": block.name,
                "input": block.input,
            }
            result = execute_tool(block.name, block.input)
            log_step(trace, iteration, "tool_result", {
                "id": block.id, "name": block.name,
                "result_preview": result[:2000],
                "result_length": len(result),
            })
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": result,
            })

        messages.append({"role": "user", "content": tool_results})

    log_step(trace, max_iterations, "max_iterations_reached", {})
    yield {
        "kind": "final",
        "answer": (
            "I wasn't able to complete the research for this question in the allowed "
            f"number of steps ({max_iterations})."
        ),
        "trace_id": trace,
        "iterations": max_iterations,
    }


def run_agent(
    user_question: str,
    trace_id: str | None = None,
    max_iterations: int = 15,
) -> AgentResponse:
    """Synchronous wrapper around ``stream_agent`` for callers that just
    want the final answer. Preserves the original API."""
    last_final: dict[str, Any] | None = None
    error_message: str | None = None
    for event in stream_agent(user_question, trace_id=trace_id, max_iterations=max_iterations):
        if event["kind"] == "error":
            error_message = event["message"]
        if event["kind"] == "final":
            last_final = event

    if error_message and last_final is None:
        # Preserve the historical exception shape for the no-key case.
        if "ANTHROPIC_API_KEY" in error_message:
            raise RuntimeError(error_message)
        return AgentResponse(answer=f"ERROR: {error_message}", trace_id="", iterations=0)

    if last_final is None:
        return AgentResponse(answer="", trace_id="", iterations=0)
    return AgentResponse(
        answer=last_final["answer"],
        trace_id=last_final["trace_id"],
        iterations=last_final["iterations"],
    )
