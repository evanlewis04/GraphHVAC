"""Model routing.

For the MVP, every query goes to the configured agent model.
"""

from __future__ import annotations

from src.config import load_settings


def pick_model(question: str) -> str:
    del question
    return load_settings().agent_model
