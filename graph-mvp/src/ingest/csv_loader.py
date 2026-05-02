"""Load ERP CSV exports into DuckDB staging tables.

Expected files in ``data/raw/``: ``skus.csv``, ``suppliers.csv``,
``customers.csv``, ``warehouses.csv``, ``inventory.csv``, ``orders.csv``.
"""

from __future__ import annotations

from pathlib import Path

import duckdb


def load_csvs(raw_dir: Path, db_path: Path) -> duckdb.DuckDBPyConnection:
    raise NotImplementedError
