"""Optional web search tool.

Disabled by default in the MVP (returns an empty list). Slot for a
real provider (Anthropic web_search server tool, Tavily, SerpAPI, etc.)
when health checks need external context.
"""

from __future__ import annotations


def web_search(query: str, max_results: int = 5) -> list[dict[str, str]]:
    del query, max_results
    return []
