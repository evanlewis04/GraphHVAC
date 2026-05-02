"""Run the canonical demo questions end-to-end and print answers + traces.

Used for the 2-minute demo video and for smoke-testing the agent loop
after prompt or tool changes.
"""

from __future__ import annotations

DEMO_QUESTIONS: list[str] = [
    "What's our exposure to the R-410A phase-out?",
    "Which customers are most affected by the recent Lennox tariff increase?",
    "Show me suppliers we depend on for more than 20% of a single category.",
    "What are good substitute parts for CAP-TURBO-200?",
]


def main() -> None:
    raise NotImplementedError


if __name__ == "__main__":
    main()
