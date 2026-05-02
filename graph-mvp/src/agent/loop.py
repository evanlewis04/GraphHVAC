"""The core agent loop - Claude with tool use, hand-rolled in ~200 lines.

No agent framework on purpose. The loop calls Claude, executes any
requested tools, appends the result to the conversation, and stops on
``end_turn`` or when ``max_iterations`` is hit. Every step writes to
the audit log.
"""

from __future__ import annotations

from dataclasses import dataclass

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
        # `thinking` field is empty unless display=summarized; keep the marker either way.
        return {"type": "thinking", "thinking": getattr(block, "thinking", "")}
    return {"type": block.type}


def _final_text(response) -> str:
    parts = [b.text for b in response.content if b.type == "text"]
    return "\n".join(p for p in parts if p).strip()


def run_agent(user_question: str, trace_id: str | None = None, max_iterations: int = 15) -> AgentResponse:
    settings = load_settings()
    if not settings.anthropic_api_key:
        raise RuntimeError("ANTHROPIC_API_KEY is not set; agent cannot run.")
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    trace = trace_id or new_trace_id()
    model = pick_model(user_question)

    log_step(trace, 0, "user_question", {"question": user_question, "model": model})

    messages: list[dict] = [{"role": "user", "content": user_question}]

    for iteration in range(1, max_iterations + 1):
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
            return AgentResponse(answer=_final_text(response), trace_id=trace, iterations=iteration)

        if response.stop_reason != "tool_use":
            return AgentResponse(
                answer=f"[stop_reason={response.stop_reason}] " + _final_text(response),
                trace_id=trace,
                iterations=iteration,
            )

        # Append the assistant turn (with tool_use blocks) to the conversation.
        messages.append({"role": "assistant", "content": response.content})

        # Execute every tool_use block and collect tool_result content.
        tool_results = []
        for block in response.content:
            if block.type != "tool_use":
                continue
            log_step(trace, iteration, "tool_call", {
                "id": block.id, "name": block.name, "input": block.input,
            })
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
    return AgentResponse(
        answer=(
            "I wasn't able to complete the research for this question in the allowed "
            f"number of steps ({max_iterations})."
        ),
        trace_id=trace,
        iterations=max_iterations,
    )
