"""Generate one markdown page per supplier with backlinks to SKUs they
provide and customers they indirectly serve."""

from __future__ import annotations

from pathlib import Path

import duckdb


def generate_all(conn: duckdb.DuckDBPyConnection, wiki_dir: Path) -> int:
    raise NotImplementedError
