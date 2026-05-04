"""Ingest raw CSVs -> DuckDB -> compile wiki. End state: ready to query.

Usage:
    python scripts/run_full_pipeline.py
    python scripts/run_full_pipeline.py --enrich-sku-limit 100   # enrich first 100 SKUs
    python scripts/run_full_pipeline.py --enrich-sku-limit -1    # enrich all SKUs (cached)
"""

from __future__ import annotations

import argparse
import time

from src.compile.compiler import compile_wiki
from src.config import load_settings
from src.ingest.csv_loader import load_csvs


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--enrich-sku-limit",
        type=int,
        default=0,
        help=(
            "Number of SKU pages to enrich with LLM-written narrative. "
            "0 (default) = none; N = first N SKUs; -1 = all SKUs. "
            "Requires ANTHROPIC_API_KEY. Cached, so re-runs are free."
        ),
    )
    args = parser.parse_args()

    settings = load_settings()
    t0 = time.time()
    conn = load_csvs(settings.raw_dir, settings.duckdb_path)
    t1 = time.time()
    print(f"Ingest: {t1 - t0:.1f}s")

    counts = compile_wiki(conn, settings.wiki_dir, enrich_sku_limit=args.enrich_sku_limit)
    t2 = time.time()
    print(f"Wiki compile: {t2 - t1:.1f}s")
    print(f"Pages written: {counts}")
    print(f"Wiki at: {settings.wiki_dir}")


if __name__ == "__main__":
    main()
