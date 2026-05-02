"""Top-level wiki compilation pipeline.

DuckDB staging tables in -> markdown wiki out. Idempotent on re-run for
the MVP (rewrites every page); incremental compilation is a later concern.
"""

from __future__ import annotations

from pathlib import Path

import duckdb

from src.compile import customer_pages, index_pages, sku_pages, supplier_pages
from src.compile.narrative import (
    Narrative,
    NarrativeCache,
    enrich_sku,
    make_client,
)
from src.config import load_settings


def _build_enricher(enrich_sku_limit: int):
    """Return (enricher, enrich_limit) for sku_pages.generate_all, or (None, None)
    when LLM enrichment is disabled."""
    if enrich_sku_limit == 0:
        return None, None

    settings = load_settings()
    client = make_client()
    cache = NarrativeCache(settings.data_dir / "narrative_cache.sqlite")

    def enricher(sku: dict, candidates: list[dict]) -> Narrative | None:
        return enrich_sku(sku, candidates, cache, client, settings.compiler_model)

    limit = None if enrich_sku_limit < 0 else enrich_sku_limit
    return enricher, limit


def compile_wiki(
    conn: duckdb.DuckDBPyConnection,
    wiki_dir: Path,
    enrich_sku_limit: int = 0,
) -> dict[str, int]:
    """Compile the full wiki.

    ``enrich_sku_limit``:
      - 0  -> no LLM calls; SKU pages use deterministic template fallback (default)
      - N  -> LLM-enrich the first N SKUs, fall back for the rest
      - -1 -> enrich every SKU (full $$$ run; cached so reruns are free)
    """
    wiki_dir.mkdir(parents=True, exist_ok=True)
    enricher, limit = _build_enricher(enrich_sku_limit)

    counts = {
        "skus": sku_pages.generate_all(conn, wiki_dir, enricher=enricher, enrich_limit=limit),
        "suppliers": supplier_pages.generate_all(conn, wiki_dir),
        "customers": customer_pages.generate_all(conn, wiki_dir),
    }
    index_pages.generate_concept_pages(conn, wiki_dir)
    index_pages.generate_indexes(wiki_dir)
    counts["warehouses"] = len(list((wiki_dir / "warehouses").glob("*.md")))
    counts["refrigerants"] = len(list((wiki_dir / "refrigerants").glob("*.md")))
    counts["concepts"] = len(list((wiki_dir / "concepts").glob("*.md")))
    return counts
