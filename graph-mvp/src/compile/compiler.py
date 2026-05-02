"""Top-level wiki compilation pipeline.

DuckDB staging tables in -> markdown wiki out. Idempotent on re-run for
the MVP (rewrites every page); incremental compilation is a later concern.
"""

from __future__ import annotations

from pathlib import Path

import duckdb

from src.compile import customer_pages, index_pages, sku_pages, supplier_pages


def compile_wiki(conn: duckdb.DuckDBPyConnection, wiki_dir: Path) -> dict[str, int]:
    wiki_dir.mkdir(parents=True, exist_ok=True)
    counts = {
        "skus": sku_pages.generate_all(conn, wiki_dir),
        "suppliers": supplier_pages.generate_all(conn, wiki_dir),
        "customers": customer_pages.generate_all(conn, wiki_dir),
    }
    index_pages.generate_concept_pages(conn, wiki_dir)
    index_pages.generate_indexes(wiki_dir)
    counts["warehouses"] = len(list((wiki_dir / "warehouses").glob("*.md")))
    counts["refrigerants"] = len(list((wiki_dir / "refrigerants").glob("*.md")))
    counts["concepts"] = len(list((wiki_dir / "concepts").glob("*.md")))
    return counts
