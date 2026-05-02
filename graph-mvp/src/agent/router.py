"""Model routing.

For the MVP, every query goes to the configured agent model
(default: claude-opus-4-7). The router exists as a thin shim so we can
drop in Sonnet/Haiku/Together routing at customer 3-5 without touching
the loop.
"""

from __future__ import annotations


def pick_model(question: str) -> str:
    raise NotImplementedError
