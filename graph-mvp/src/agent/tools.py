"""Tool schemas (Anthropic tool-use format) and the dispatcher that
maps a tool name to a Python callable in ``src/tools/``."""

from __future__ import annotations

import json
from typing import Any

from src.tools.sql_query import get_schema, run_sql
from src.tools.wiki_read import list_wiki_directory, read_wiki_page, search_wiki

AGENT_TOOLS: list[dict[str, Any]] = [
    {
        "name": "read_wiki_page",
        "description": (
            "Read the full contents of a wiki page by its relative path "
            "(e.g. 'skus/CAP-LEN-30MFD-0001.md', 'concepts/r-410a-phase-out.md', '_index.md')."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
            },
            "required": ["path"],
        },
    },
    {
        "name": "search_wiki",
        "description": (
            "Substring search across all wiki pages. Returns matching pages with snippets. "
            "Use single keywords or short phrases - 'R-410A', 'Lennox tariff', 'capacitor'."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "limit": {"type": "integer", "default": 20},
            },
            "required": ["query"],
        },
    },
    {
        "name": "list_wiki_directory",
        "description": (
            "List the files in a wiki subdirectory. Useful starting points: '', 'skus', "
            "'suppliers', 'customers', 'warehouses', 'refrigerants', 'concepts'."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "directory": {"type": "string"},
            },
            "required": ["directory"],
        },
    },
    {
        "name": "run_sql",
        "description": (
            "Run a read-only DuckDB SQL query. Available tables: suppliers, warehouses, skus, "
            "customers, orders, inventory. Use this for counts, sums, top-N, joins, and any "
            "numeric question. Returns at most 200 rows; aggregate or LIMIT in your query."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
            },
            "required": ["query"],
        },
    },
    {
        "name": "get_schema",
        "description": "Get the column-and-type list for one DuckDB table.",
        "input_schema": {
            "type": "object",
            "properties": {
                "table": {"type": "string"},
            },
            "required": ["table"],
        },
    },
]


def execute_tool(name: str, arguments: dict[str, Any]) -> str:
    """Execute a tool and return its result as a string for tool_result content."""
    try:
        if name == "read_wiki_page":
            return read_wiki_page(arguments["path"])
        if name == "search_wiki":
            results = search_wiki(arguments["query"], arguments.get("limit", 20))
            return json.dumps(results, indent=2)
        if name == "list_wiki_directory":
            return json.dumps(list_wiki_directory(arguments["directory"]), indent=2)
        if name == "run_sql":
            rows = run_sql(arguments["query"])
            return json.dumps(rows, indent=2, default=str)
        if name == "get_schema":
            return json.dumps(get_schema(arguments["table"]), indent=2)
        return f"ERROR: unknown tool {name}"
    except Exception as exc:  # surface failures to the model so it can adapt
        return f"ERROR: {type(exc).__name__}: {exc}"
