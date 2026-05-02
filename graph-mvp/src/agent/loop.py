"""The core agent loop — Claude with tool use, hand-rolled in ~200 lines.

No agent framework on purpose. The loop calls Claude, executes any
requested tools, appends the result to the conversation, and stops on
``end_turn`` or when ``max_iterations`` is hit. Every step writes to
the audit log.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class AgentResponse:
    answer: str
    trace_id: str
    iterations: int


def run_agent(user_question: str, trace_id: str, max_iterations: int = 15) -> AgentResponse:
    raise NotImplementedError
