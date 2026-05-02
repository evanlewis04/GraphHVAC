"""Optional web search tool, off by default in the MVP.

Used during health checks and imputation (e.g., "what's the current EPA
status of refrigerant X?"). Disabled when no provider key is configured.
"""

from __future__ import annotations


def web_search(query: str, max_results: int = 5) -> list[dict[str, str]]:
    raise NotImplementedError
