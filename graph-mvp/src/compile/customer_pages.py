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


def _prefetch_top_skus(conn: duckdb.DuckDBPyConnection, k: int = 10) -> dict[str, list[dict]]:
    rows = conn.execute(
        f"""
        WITH agg AS (
            SELECT customer_id, sku_id,
                   SUM(qty)            AS units,
                   SUM(extended_price) AS revenue
            FROM orders
            GROUP BY customer_id, sku_id
        ),
        ranked AS (
            SELECT *, ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY revenue DESC) AS rn
            FROM agg
        )
        SELECT customer_id, sku_id, units, revenue
        FROM ranked WHERE rn <= {k}
        ORDER BY customer_id, rn
        """
    ).fetchall()
    out: dict[str, list[dict]] = {}
    for cust_id, sku_id, units, revenue in rows:
        out.setdefault(cust_id, []).append(
            {"sku_id": sku_id, "units": units, "revenue": revenue}
        )
    return out


def _prefetch_refrigerant_mix(conn: duckdb.DuckDBPyConnection) -> dict[str, list[dict]]:
    rows = conn.execute(
        """
        SELECT o.customer_id, s.refrigerant, SUM(o.extended_price) AS revenue
        FROM orders o JOIN skus s ON o.sku_id = s.id
        WHERE s.refrigerant IS NOT NULL
        GROUP BY 1, 2
        ORDER BY 1, revenue DESC
        """
    ).fetchall()
    out: dict[str, list[dict]] = {}
    for cust_id, rfg, rev in rows:
        out.setdefault(cust_id, []).append({"refrigerant": rfg, "revenue": rev})
    return out


def _prefetch_summary(conn: duckdb.DuckDBPyConnection) -> dict[str, dict]:
    rows = conn.execute(
        """
        SELECT customer_id,
               COUNT(DISTINCT order_id)            AS orders,
               COALESCE(SUM(extended_price), 0.0)  AS revenue
        FROM orders
        GROUP BY customer_id
        """
    ).fetchall()
    return {cid: {"orders": orders, "revenue": revenue} for cid, orders, revenue in rows}


def generate_all(conn: duckdb.DuckDBPyConnection, wiki_dir: Path) -> int:
    out_dir = wiki_dir / "customers"
    out_dir.mkdir(parents=True, exist_ok=True)

    customers = conn.execute("SELECT * FROM customers").fetchdf().to_dict("records")
    top_skus_by_cust = _prefetch_top_skus(conn)
    rfg_mix_by_cust = _prefetch_refrigerant_mix(conn)
    summary_by_cust = _prefetch_summary(conn)

    count = 0
    for cust in tqdm(customers, desc="customer pages", unit="page"):
        top_skus = top_skus_by_cust.get(cust["id"], [])
        refrigerant_mix = rfg_mix_by_cust.get(cust["id"], [])
        summary = summary_by_cust.get(cust["id"], {"orders": 0, "revenue": 0.0})
        page = _render(cust, top_skus, refrigerant_mix, summary)
        (out_dir / f"{cust['id']}.md").write_text(page, encoding="utf-8")
        count += 1
    return count
