"""Run the canonical demo questions end-to-end and print answers + traces.

Used for the 2-minute demo video and for smoke-testing the agent loop
after prompt or tool changes. Requires ANTHROPIC_API_KEY.
"""

from __future__ import annotations

import sys

from src.agent.loop import run_agent
from src.audit.logger import fetch_trace

DEMO_QUESTIONS: list[str] = [
    "What's our exposure to the R-410A phase-out? Which 5 customers are most affected?",
    "Show me suppliers we depend on for more than 20% of a single category.",
    "What are the top 5 customers by revenue, and what segments are they in?",
    "How many capacitors do we stock at the Atlanta warehouse, and what's the total on-hand value?",
]


def main() -> None:
    questions = sys.argv[1:] or DEMO_QUESTIONS
    for q in questions:
        print(f"\n{'=' * 80}\nQ: {q}\n{'=' * 80}")
        result = run_agent(q)
        print(f"\nA ({result.iterations} iter, trace {result.trace_id}):\n{result.answer}")
        trace = fetch_trace(result.trace_id)
        tool_calls = [s for s in trace if s["kind"] == "tool_call"]
        print(f"\nTools used: {[t['payload']['name'] for t in tool_calls]}")


if __name__ == "__main__":
    main()
