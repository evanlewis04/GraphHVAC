"""Generate one markdown page per customer with backlinks to top SKUs
they buy and concentration metrics."""

from __future__ import annotations

from pathlib import Path

import duckdb
from tqdm import tqdm


def _render(customer: dict, top_skus: list[dict], refrigerant_mix: list[dict], summary: dict) -> str:
    sku_lines = "\n".join(
        f"- [[skus/{r['sku_id']}]] - {r['units']} units, ${r['revenue']:,.0f}"
        for r in top_skus
    ) or "- _No order history._"
    rfg_lines = "\n".join(
        f"- [[refrigerants/{r['refrigerant'].lower().replace(' ', '-')}]]: ${r['revenue']:,.0f}"
        for r in refrigerant_mix if r["refrigerant"]
    ) or "- _No refrigerant exposure on record._"
    return f"""---
type: customer
id: {customer['id']}
segment: {customer['segment']}
region: {customer['region']}
---

# {customer['name']}

**Segment:** {customer['segment']}
**Region:** {customer['region']}
**Primary warehouse:** [[warehouses/{customer['primary_warehouse_id']}]]
**24-month revenue:** ${summary['revenue']:,.0f} across {summary['orders']} orders

## Top SKUs purchased
{sku_lines}

## Refrigerant exposure
{rfg_lines}

## Sources
- DuckDB: `SELECT * FROM customers WHERE id = '{customer['id']}'`
- DuckDB: `SELECT sku_id, SUM(qty), SUM(extended_price) FROM orders WHERE customer_id = '{customer['id']}' GROUP BY 1 ORDER BY 3 DESC`
"""


def generate_all(conn: duckdb.DuckDBPyConnection, wiki_dir: Path) -> int:
    out_dir = wiki_dir / "customers"
    out_dir.mkdir(parents=True, exist_ok=True)

    customers = conn.execute("SELECT * FROM customers").fetchdf().to_dict("records")
    count = 0
    for cust in tqdm(customers, desc="customer pages", unit="page"):
        top_skus = conn.execute(
            """
            SELECT sku_id, SUM(qty) AS units, SUM(extended_price) AS revenue
            FROM orders WHERE customer_id = ?
            GROUP BY 1 ORDER BY revenue DESC LIMIT 10
            """,
            [cust["id"]],
        ).fetchdf().to_dict("records")
        refrigerant_mix = conn.execute(
            """
            SELECT s.refrigerant, SUM(o.extended_price) AS revenue
            FROM orders o JOIN skus s ON o.sku_id = s.id
            WHERE o.customer_id = ? AND s.refrigerant IS NOT NULL
            GROUP BY 1 ORDER BY 2 DESC
            """,
            [cust["id"]],
        ).fetchdf().to_dict("records")
        summary_row = conn.execute(
            """
            SELECT COUNT(DISTINCT order_id) AS orders, COALESCE(SUM(extended_price), 0) AS revenue
            FROM orders WHERE customer_id = ?
            """,
            [cust["id"]],
        ).fetchone()
        summary = {"orders": summary_row[0], "revenue": summary_row[1]}
        page = _render(cust, top_skus, refrigerant_mix, summary)
        (out_dir / f"{cust['id']}.md").write_text(page, encoding="utf-8")
        count += 1
    return count
