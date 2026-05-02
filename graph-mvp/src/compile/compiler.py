"""Top-level wiki compilation pipeline.

DuckDB staging tables in -> markdown wiki out. Idempotent on re-run for
the MVP (rewrites every page); incremental compilation is a later concern.
"""

from __future__ import annotations

from pathlib import Path

import duckdb


def compile_wiki(conn: duckdb.DuckDBPyConnection, wiki_dir: Path) -> None:
    raise NotImplementedError
