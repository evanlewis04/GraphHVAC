"""Generate one markdown page per SKU.

Each page combines templated structure (identity, supplier, manufacturer,
pricing band, warehouse availability) with LLM-written narrative
(description, substitute candidates, regulatory/refrigerant notes).
Backlinks point to the SKU's supplier, manufacturer, warehouse, and any
referenced concept pages.
"""

from __future__ import annotations

from pathlib import Path

import duckdb


def generate_all(conn: duckdb.DuckDBPyConnection, wiki_dir: Path) -> int:
    raise NotImplementedError
