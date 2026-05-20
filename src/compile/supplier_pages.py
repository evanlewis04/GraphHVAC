"""Generate one markdown page per supplier with backlinks to SKUs they
provide and customers they indirectly serve."""

from __future__ import annotations

from pathlib import Path

import duckdb
from tqdm import tqdm


def _render(supplier: dict, categories: list[dict], top_skus: list[dict], total_skus: int) -> str:
    cat_lines = "\n".join(
        f"- **{r['category']}**: {r['n_skus']} SKUs, ${r['total_revenue']:,.0f} revenue (24mo)"
        for r in categories
    ) or "- _No SKUs._"
    sku_lines = "\n".join(
        f"- [[skus/{r['id']}]] - {r['name']} (${r['revenue']:,.0f})"
        for r in top_skus
    ) or "- _No top SKUs._"
    type_label = "Master Distributor" if supplier.get("is_master") else "Specialty Distributor"
    return f"""---
type: supplier
id: {supplier['id']}
is_master: {bool(supplier.get('is_master'))}
---

# {supplier['name']}

**Type:** {type_label}
**Primary category:** {supplier['primary_category']}
**Total SKUs sourced:** {total_skus}

## Categories supplied
{cat_lines}

## Top SKUs we source from them (last 24 months by revenue)
{sku_lines}

## Concentration notes
{
    "This is a **master distributor** — broad catalog coverage across categories. "
    "Concentration risk is low for any individual SKU but high for overall supply continuity."
    if supplier.get('is_master')
    else f"Specialty supplier focused on {supplier['primary_category']}. Concentration risk is "
         f"category-specific - a disruption here would primarily affect that line."
}

## Sources
- DuckDB: `SELECT * FROM suppliers WHERE id = '{supplier['id']}'`
- DuckDB: `SELECT category, COUNT(*) FROM skus WHERE primary_supplier_id = '{supplier['id']}' GROUP BY 1`
- DuckDB: `SELECT s.id, s.name, SUM(o.extended_price) FROM orders o JOIN skus s ON o.sku_id=s.id WHERE s.primary_supplier_id = '{supplier['id']}' GROUP BY 1,2 ORDER BY 3 DESC LIMIT 25`
"""


def generate_all(conn: duckdb.DuckDBPyConnection, wiki_dir: Path) -> int:
    out_dir = wiki_dir / "suppliers"
    out_dir.mkdir(parents=True, exist_ok=True)

    suppliers = conn.execute("SELECT * FROM suppliers").fetchdf().to_dict("records")
    count = 0
    for sup in tqdm(suppliers, desc="supplier pages", unit="page"):
        cats = conn.execute(
            """
            SELECT s.category,
                   COUNT(DISTINCT s.id) AS n_skus,
                   COALESCE(SUM(o.extended_price), 0) AS total_revenue
            FROM skus s LEFT JOIN orders o ON o.sku_id = s.id
            WHERE s.primary_supplier_id = ?
            GROUP BY 1 ORDER BY total_revenue DESC
            """,
            [sup["id"]],
        ).fetchdf().to_dict("records")
        top_skus = conn.execute(
            """
            SELECT s.id, s.name, COALESCE(SUM(o.extended_price), 0) AS revenue
            FROM skus s LEFT JOIN orders o ON o.sku_id = s.id
            WHERE s.primary_supplier_id = ?
            GROUP BY 1, 2 ORDER BY revenue DESC LIMIT 10
            """,
            [sup["id"]],
        ).fetchdf().to_dict("records")
        total = conn.execute(
            "SELECT COUNT(*) FROM skus WHERE primary_supplier_id = ?",
            [sup["id"]],
        ).fetchone()[0]
        page = _render(sup, cats, top_skus, total)
        (out_dir / f"{sup['id']}.md").write_text(page, encoding="utf-8")
        count += 1
    return count
