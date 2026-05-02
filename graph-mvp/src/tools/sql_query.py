"""SQL tools.

``run_sql`` executes a read-only query against the staging DuckDB and
returns rows as a list of dicts (truncated to a sane row cap so the
agent doesn't burn context on a 10k-row dump). ``get_schema`` returns
the column-and-type list for a single table.
"""

from __future__ import annotations

from typing import Any


def run_sql(query: str, max_rows: int = 200) -> list[dict[str, Any]]:
    raise NotImplementedError


def get_schema(table: str) -> list[dict[str, str]]:
    raise NotImplementedError
