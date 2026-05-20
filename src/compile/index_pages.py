"""Generate the top-level _index.md, per-section index pages, warehouse
pages, refrigerant pages, and concept pages (cross-cutting analyses).
"""

from __future__ import annotations

from pathlib import Path

import duckdb


REFRIGERANTS = [
    ("R-22", "r-22", "Phased out for new equipment under EPA SNAP. Service-only; "
     "production banned in the US since 2020. Customers running R-22 systems are "
     "candidates for replacement equipment quotes."),
    ("R-410A", "r-410a", "Under HFC phase-down per the AIM Act (2020). Manufacture "
     "of new residential R-410A equipment is banned starting January 2025. Existing "
     "stock and service refills remain legal but supply is tightening; expect "
     "reagent price escalation through 2025-2026."),
    ("R-32", "r-32", "Mildly flammable (A2L) HFC replacement, ~68% lower GWP than R-410A. "
     "Adopted by Daikin and Mitsubishi early; broader US uptake accelerating."),
    ("R-454B", "r-454b", "A2L HFO blend used in newer Carrier, Lennox, Trane equipment "
     "post-2025 transition. ~78% lower GWP than R-410A."),
    ("R-1234yf", "r-1234yf", "HFO refrigerant; primarily mobile/automotive A/C, limited "
     "stationary HVAC use."),
]


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _generate_warehouse_pages(conn: duckdb.DuckDBPyConnection, wiki_dir: Path) -> None:
    out = wiki_dir / "warehouses"
    out.mkdir(parents=True, exist_ok=True)
    warehouses = conn.execute("SELECT * FROM warehouses").fetchdf().to_dict("records")
    for wh in warehouses:
        stats = conn.execute(
            """
            SELECT COUNT(*) AS skus, SUM(qty_on_hand) AS units
            FROM inventory WHERE warehouse_id = ?
            """,
            [wh["id"]],
        ).fetchone()
        top_cats = conn.execute(
            """
            SELECT s.category, SUM(i.qty_on_hand) AS units
            FROM inventory i JOIN skus s ON i.sku_id = s.id
            WHERE i.warehouse_id = ? GROUP BY 1 ORDER BY 2 DESC
            """,
            [wh["id"]],
        ).fetchdf().to_dict("records")
        cat_lines = "\n".join(f"- {r['category']}: {r['units']:,} units" for r in top_cats)
        _write(out / f"{wh['id']}.md", f"""---
type: warehouse
id: {wh['id']}
state: {wh['state']}
---

# {wh['name']} ({wh['id']})

**State:** {wh['state']}
**SKUs stocked:** {stats[0]:,}
**Total units on hand:** {stats[1]:,}

## Inventory by category
{cat_lines}

## Sources
- DuckDB: `SELECT * FROM inventory WHERE warehouse_id = '{wh['id']}'`
""")


def _generate_refrigerant_pages(conn: duckdb.DuckDBPyConnection, wiki_dir: Path) -> None:
    out = wiki_dir / "refrigerants"
    out.mkdir(parents=True, exist_ok=True)
    for code, slug, note in REFRIGERANTS:
        sku_count = conn.execute(
            "SELECT COUNT(*) FROM skus WHERE refrigerant = ?", [code]
        ).fetchone()[0]
        revenue = conn.execute(
            """
            SELECT COALESCE(SUM(o.extended_price), 0)
            FROM orders o JOIN skus s ON o.sku_id = s.id
            WHERE s.refrigerant = ?
            """,
            [code],
        ).fetchone()[0]
        top_customers = conn.execute(
            """
            SELECT o.customer_id, c.name, SUM(o.extended_price) AS revenue
            FROM orders o JOIN skus s ON o.sku_id = s.id
            JOIN customers c ON c.id = o.customer_id
            WHERE s.refrigerant = ?
            GROUP BY 1, 2 ORDER BY 3 DESC LIMIT 10
            """,
            [code],
        ).fetchdf().to_dict("records")
        cust_lines = "\n".join(
            f"- [[customers/{r['customer_id']}]] {r['name']} - ${r['revenue']:,.0f}"
            for r in top_customers
        )
        _write(out / f"{slug}.md", f"""---
type: refrigerant
code: {code}
---

# Refrigerant {code}

{note}

**SKUs tied to {code}:** {sku_count}
**24-month revenue from {code}-tied SKUs:** ${revenue:,.0f}

## Top customers exposed to {code}
{cust_lines or "_None on record._"}

## Sources
- DuckDB: `SELECT COUNT(*) FROM skus WHERE refrigerant = '{code}'`
- DuckDB: `SELECT customer_id, SUM(extended_price) FROM orders o JOIN skus s ON o.sku_id=s.id WHERE s.refrigerant = '{code}' GROUP BY 1 ORDER BY 2 DESC`
""")


def _generate_concept_pages(conn: duckdb.DuckDBPyConnection, wiki_dir: Path) -> None:
    out = wiki_dir / "concepts"
    out.mkdir(parents=True, exist_ok=True)

    # R-410A phase-out exposure
    r410a = conn.execute(
        """
        SELECT c.id, c.name, c.segment, c.region, SUM(o.extended_price) AS exposure
        FROM orders o JOIN skus s ON o.sku_id = s.id
        JOIN customers c ON c.id = o.customer_id
        WHERE s.refrigerant = 'R-410A'
        GROUP BY 1, 2, 3, 4 ORDER BY exposure DESC LIMIT 25
        """
    ).fetchdf().to_dict("records")
    total_exposure = conn.execute(
        """
        SELECT SUM(o.extended_price)
        FROM orders o JOIN skus s ON o.sku_id = s.id
        WHERE s.refrigerant = 'R-410A'
        """
    ).fetchone()[0] or 0
    lines = "\n".join(
        f"| [[customers/{r['id']}]] | {r['name']} | {r['segment']} | {r['region']} | ${r['exposure']:,.0f} |"
        for r in r410a
    )
    _write(out / "r-410a-phase-out.md", f"""---
type: concept
topic: R-410A phase-out exposure
---

# R-410A Phase-Out Exposure

The HFC phase-down under the AIM Act bans manufacture of new R-410A residential
equipment starting January 2025. Service refills and existing inventory remain
legal but tighten quickly. Customers concentrated on R-410A-tied SKUs need
replacement-system quotes (R-32 or R-454B) and refrigerant pre-buy guidance.

**Total 24-month revenue from R-410A-tied SKUs:** ${total_exposure:,.0f}

## Top 25 customers by R-410A exposure

| Customer | Name | Segment | Region | 24mo R-410A revenue |
|---|---|---|---|---|
{lines}

## Recommended actions
- Outreach to top-10 customers for replacement equipment quotes (route to [[refrigerants/r-32]] or [[refrigerants/r-454b]])
- Refrigerant pre-buy guidance ahead of Q4 price escalation
- Inventory triage: drawdown plan for R-410A SKUs at warehouses (see [[warehouses/]] pages)

## Sources
- DuckDB: `SELECT customer_id, SUM(extended_price) FROM orders o JOIN skus s ON o.sku_id=s.id WHERE s.refrigerant='R-410A' GROUP BY 1 ORDER BY 2 DESC`
- See also: [[refrigerants/r-410a]], [[concepts/supplier-concentration]]
""")

    # Supplier concentration
    sup_conc = conn.execute(
        """
        SELECT s.primary_supplier_id AS supplier_id,
               sup.name AS supplier_name,
               s.category,
               COUNT(DISTINCT s.id) AS skus_in_cat,
               SUM(o.extended_price) AS revenue
        FROM skus s
        JOIN suppliers sup ON sup.id = s.primary_supplier_id
        LEFT JOIN orders o ON o.sku_id = s.id
        GROUP BY 1, 2, 3
        HAVING revenue > 0
        ORDER BY revenue DESC LIMIT 50
        """
    ).fetchdf().to_dict("records")
    rows = "\n".join(
        f"| [[suppliers/{r['supplier_id']}]] | {r['supplier_name']} | {r['category']} | "
        f"{r['skus_in_cat']} | ${r['revenue']:,.0f} |"
        for r in sup_conc
    )
    _write(out / "supplier-concentration.md", f"""---
type: concept
topic: Supplier concentration
---

# Supplier Concentration

Where one supplier accounts for an outsized share of a single category, a
disruption (price hike, allocation cut, M&A) becomes an immediate operational
issue. This page lists the top supplier x category cells by revenue so the
operating team can see where second-source effort would pay off.

## Top supplier-category combinations (last 24 months)

| Supplier | Name | Category | SKUs | Revenue |
|---|---|---|---|---|
{rows}

## Sources
- DuckDB: `SELECT primary_supplier_id, category, COUNT(*), SUM(extended_price) FROM skus JOIN orders USING(sku_id... -- see query above`
""")

    # Top customers by revenue
    top_cust = conn.execute(
        """
        SELECT c.id, c.name, c.segment, c.region,
               SUM(o.extended_price) AS revenue,
               COUNT(DISTINCT o.order_id) AS orders
        FROM customers c JOIN orders o ON o.customer_id = c.id
        GROUP BY 1, 2, 3, 4 ORDER BY revenue DESC LIMIT 25
        """
    ).fetchdf().to_dict("records")
    rows = "\n".join(
        f"| [[customers/{r['id']}]] | {r['name']} | {r['segment']} | {r['region']} | "
        f"${r['revenue']:,.0f} | {r['orders']} |"
        for r in top_cust
    )
    _write(out / "top-customers-by-revenue.md", f"""---
type: concept
topic: Top customers by revenue
---

# Top 25 Customers by Revenue (last 24 months)

| Customer | Name | Segment | Region | Revenue | Orders |
|---|---|---|---|---|---|
{rows}
""")


def generate_indexes(wiki_dir: Path) -> None:
    """Regenerate the top-level _index.md and per-section index pages.

    Per-section indexes link to the section's directory rather than every
    file - Obsidian's directory listing is the right viewer for thousands
    of pages, and listing 5,000 SKUs in a markdown file is unreadable.
    """
    sections = ["skus", "suppliers", "customers", "warehouses", "refrigerants", "concepts"]
    section_lines = "\n".join(
        f"- [[{section}/]] - browse all {section}" for section in sections
    )
    _write(wiki_dir / "_index.md", f"""# Graph Wiki

This vault is the living operational wiki for the distributor. Every page is
generated by Graph's compilation pipeline; treat hand-edits as temporary.

## Sections
{section_lines}

## Cross-cutting analyses (concepts/)
- [[concepts/r-410a-phase-out]]
- [[concepts/supplier-concentration]]
- [[concepts/top-customers-by-revenue]]

## How answers are sourced

Every answer the chat produces cites the wiki pages it read and the SQL
queries it ran. Click "Show sources" in the chat to see the full trace.
""")


def generate_concept_pages(conn: duckdb.DuckDBPyConnection, wiki_dir: Path) -> None:
    """Public entry point: warehouse + refrigerant + concept pages."""
    _generate_warehouse_pages(conn, wiki_dir)
    _generate_refrigerant_pages(conn, wiki_dir)
    _generate_concept_pages(conn, wiki_dir)
