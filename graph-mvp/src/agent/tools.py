"""Tool schemas (Anthropic tool-use format) and the dispatcher that
maps a tool name to a Python callable in ``src/tools/``."""

from __future__ import annotations

from typing import Any

AGENT_TOOLS: list[dict[str, Any]] = [
    # read_wiki_page, search_wiki, list_wiki_directory, run_sql, get_schema
    # — populated when the loop is implemented.
]


def execute_tool(name: str, arguments: dict[str, Any]) -> str:
    raise NotImplementedError
