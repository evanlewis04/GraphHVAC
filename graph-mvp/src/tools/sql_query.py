"""SQL tools.

``run_sql`` executes a read-only query against the staging DuckDB and
returns rows as a list of dicts (truncated to a sane row cap so the
agent doesn't burn context on a 10k-row dump). ``get_schema`` returns
the column-and-type list for a single table.
"""

from __future__ import annotations

from typing import Any

import duckdb

from src.config import load_settings


def _connect() -> duckdb.DuckDBPyConnection:
    settings = load_settings()
    if not settings.duckdb_path.exists():
        raise FileNotFoundError(
            f"DuckDB at {settings.duckdb_path} does not exist. "
            "Run scripts/run_full_pipeline.py first."
        )
    return duckdb.connect(str(settings.duckdb_path), read_only=True)


def run_sql(query: str, max_rows: int = 200) -> list[dict[str, Any]]:
    conn = _connect()
    try:
        cursor = conn.execute(query)
        cols = [d[0] for d in cursor.description] if cursor.description else []
        rows = cursor.fetchmany(max_rows)
        return [dict(zip(cols, r)) for r in rows]
    finally:
        conn.close()


def get_schema(table: str) -> list[dict[str, str]]:
    conn = _connect()
    try:
        cursor = conn.execute(f"DESCRIBE {table}")
        cols = [d[0] for d in cursor.description]
        rows = cursor.fetchall()
        return [dict(zip(cols, r)) for r in rows]
    finally:
        conn.close()
