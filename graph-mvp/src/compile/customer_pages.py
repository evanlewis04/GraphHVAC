"""Generate one markdown page per customer with backlinks to top SKUs
they buy and concentration metrics."""

from __future__ import annotations

from pathlib import Path

import duckdb


def generate_all(conn: duckdb.DuckDBPyConnection, wiki_dir: Path) -> int:
    raise NotImplementedError
