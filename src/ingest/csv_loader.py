"""Load ERP CSV exports into DuckDB staging tables.

Expected files in ``data/raw/``: ``skus.csv``, ``suppliers.csv``,
``customers.csv``, ``warehouses.csv``, ``inventory.csv``, ``orders.csv``.
"""

from __future__ import annotations

from pathlib import Path

import duckdb

TABLES = ["suppliers", "warehouses", "skus", "customers", "orders", "inventory"]


def load_csvs(raw_dir: Path, db_path: Path) -> duckdb.DuckDBPyConnection:
    """Replace each staging table from its CSV. Returns the open connection."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = duckdb.connect(str(db_path))

    for table in TABLES:
        csv_path = raw_dir / f"{table}.csv"
        if not csv_path.exists():
            raise FileNotFoundError(
                f"Missing {csv_path}. Run scripts/generate_synthetic_data.py first."
            )
        conn.execute(f"DROP TABLE IF EXISTS {table}")
        conn.execute(
            f"CREATE TABLE {table} AS SELECT * FROM read_csv_auto(?, header=true)",
            [str(csv_path)],
        )

    counts = {t: conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0] for t in TABLES}
    print(f"Loaded into {db_path}: {counts}")
    return conn
