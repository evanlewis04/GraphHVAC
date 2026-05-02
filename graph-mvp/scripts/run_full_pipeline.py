"""Ingest raw CSVs -> DuckDB -> compile wiki. End state: ready to query.

Usage:
    python scripts/run_full_pipeline.py
"""

from __future__ import annotations

import time

from src.compile.compiler import compile_wiki
from src.config import load_settings
from src.ingest.csv_loader import load_csvs


def main() -> None:
    settings = load_settings()
    t0 = time.time()
    conn = load_csvs(settings.raw_dir, settings.duckdb_path)
    t1 = time.time()
    print(f"Ingest: {t1 - t0:.1f}s")

    counts = compile_wiki(conn, settings.wiki_dir)
    t2 = time.time()
    print(f"Wiki compile: {t2 - t1:.1f}s")
    print(f"Pages written: {counts}")
    print(f"Wiki at: {settings.wiki_dir}")


if __name__ == "__main__":
    main()
