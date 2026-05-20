"""Generate one markdown page per SKU.

Each page combines templated structure (identity, supplier, manufacturer,
pricing band, warehouse availability) with optional LLM-written narrative
(description, substitute candidates, regulatory/refrigerant notes).
Backlinks point to the SKU's supplier, manufacturer, warehouse, and any
referenced concept pages.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Callable

import duckdb
from tqdm import tqdm

from src.compile.narrative import Narrative


def _slug(name: str) -> str:
    return re.sub(r"[^a-z0-9-]+", "-", name.lower()).strip("-")


def _refrigerant_note(refrigerant) -> str:
    # pandas converts empty CSV cells to NaN (float); coerce to None
    if refrigerant is None or (isinstance(refrigerant, float)) or not str(refrigerant).strip():
        return "_No refrigerant association on file._"
    refrigerant = str(refrigerant)
    if refrigerant in {"R-22"}:
        return f"⚠️ Tied to **[[refrigerants/{_slug(refrigerant)}]]** — fully phased out for new equipment under EPA SNAP. Service-only."
    if refrigerant == "R-410A":
        return f"⚠️ Tied to **[[refrigerants/{_slug(refrigerant)}]]** — under HFC phase-down (AIM Act). New residential equipment manufacture banned 2025."
    return f"Tied to **[[refrigerants/{_slug(refrigerant)}]]**."


def _description_section(sku: dict, supplier_name: str, narrative: Narrative | None) -> str:
    if narrative and narrative.description:
        return narrative.description.strip()
    return f"{sku['name']}. Sourced primarily from {supplier_name}."


def _refrigerant_section(sku: dict, narrative: Narrative | None) -> str:
    base = _refrigerant_note(sku.get("refrigerant"))
    if narrative and narrative.regulatory_notes:
        return f"{base}\n\n{narrative.regulatory_notes.strip()}"
    return base


def _substitutes_section(narrative: Narrative | None) -> str:
    if not narrative or not narrative.substitutes:
        return "_No suggested substitutes._"
    return "\n".join(
        f"- [[skus/{s['sku_id']}]] — {s['rationale']}"
        for s in narrative.substitutes
    )


def _render_sku_page(
    sku: dict,
    supplier_name: str,
    inventory: list[dict],
    top_customers: list[dict],
    narrative: Narrative | None = None,
) -> str:
    inventory_lines = "\n".join(
        f"- [[warehouses/{r['warehouse_id']}]]: **{r['qty_on_hand']}** on hand "
        f"(reorder at {r['reorder_point']})"
        for r in inventory
    ) or "- _No active inventory._"

    customer_lines = "\n".join(
        f"- [[customers/{r['customer_id']}]] - {r['units']} units, ${r['revenue']:,.0f}"
        for r in top_customers
    ) or "- _No order history._"

    margin = (sku["list_price"] - sku["unit_cost"]) / sku["list_price"] * 100 if sku["list_price"] else 0
    enriched_flag = "true" if narrative else "false"

    return f"""---
type: sku
id: {sku['id']}
manufacturer: {sku['manufacturer']}
category: {sku['category']}
sub_type: {sku['sub_type']}
refrigerant: {sku.get('refrigerant') if isinstance(sku.get('refrigerant'), str) else ''}
llm_enriched: {enriched_flag}
---

# {sku['id']} — {sku['name']}

**Manufacturer:** {sku['manufacturer']}
**Category:** {sku['category']} ({sku['sub_type']})
**Supplier:** [[suppliers/{sku['primary_supplier_id']}]] — {supplier_name}
**Unit cost:** ${sku['unit_cost']:.2f} | **List:** ${sku['list_price']:.2f} | **Margin:** {margin:.0f}%

## Description
{_description_section(sku, supplier_name, narrative)}

## Refrigerant exposure
{_refrigerant_section(sku, narrative)}

## Substitutes
{_substitutes_section(narrative)}

## Warehouse availability
{inventory_lines}

## Top customers (last 24 months)
{customer_lines}

## Sources
- DuckDB: `SELECT * FROM skus WHERE id = '{sku['id']}'`
- DuckDB: `SELECT * FROM inventory WHERE sku_id = '{sku['id']}'`
- DuckDB: `SELECT customer_id, SUM(qty), SUM(extended_price) FROM orders WHERE sku_id = '{sku['id']}' GROUP BY 1`
"""


def _candidate_substitutes(
    conn: duckdb.DuckDBPyConnection, sku: dict, limit: int = 12
) -> list[dict]:
    """Pull SKUs in the same category, biased toward the same sub-type and
    a different manufacturer (so the model has real alternatives to pick from)."""
    rows = conn.execute(
        """
        SELECT id, name, manufacturer, sub_type
        FROM skus
        WHERE category = ? AND id != ?
        ORDER BY (sub_type = ?) DESC, (manufacturer != ?) DESC, RANDOM()
        LIMIT ?
        """,
        [sku["category"], sku["id"], sku["sub_type"], sku["manufacturer"], limit],
    ).fetchdf().to_dict("records")
    return rows


# An "enricher" turns (sku, candidates) -> Narrative or None on failure.
Enricher = Callable[[dict, list[dict]], Narrative | None]


def _prefetch_inventory(conn: duckdb.DuckDBPyConnection) -> dict[str, list[dict]]:
    """One query, group rows in Python — faster than 5,000 per-SKU queries."""
    rows = conn.execute(
        "SELECT sku_id, warehouse_id, qty_on_hand, reorder_point "
        "FROM inventory ORDER BY sku_id, warehouse_id"
    ).fetchall()
    out: dict[str, list[dict]] = {}
    for sku_id, wh, qty, rp in rows:
        out.setdefault(sku_id, []).append(
            {"warehouse_id": wh, "qty_on_hand": qty, "reorder_point": rp}
        )
    return out


def _prefetch_top_customers(conn: duckdb.DuckDBPyConnection, k: int = 5) -> dict[str, list[dict]]:
    """Top-K customers per SKU by revenue. Uses a window function so the
    grouping happens in DuckDB (one scan of orders), not in Python."""
    rows = conn.execute(
        f"""
        WITH agg AS (
            SELECT sku_id, customer_id,
                   SUM(qty)            AS units,
                   SUM(extended_price) AS revenue
            FROM orders
            GROUP BY sku_id, customer_id
        ),
        ranked AS (
            SELECT *, ROW_NUMBER() OVER (PARTITION BY sku_id ORDER BY revenue DESC) AS rn
            FROM agg
        )
        SELECT sku_id, customer_id, units, revenue
        FROM ranked WHERE rn <= {k}
        ORDER BY sku_id, rn
        """
    ).fetchall()
    out: dict[str, list[dict]] = {}
    for sku_id, cust_id, units, revenue in rows:
        out.setdefault(sku_id, []).append(
            {"customer_id": cust_id, "units": units, "revenue": revenue}
        )
    return out


def _prefetch_substitute_candidates(
    conn: duckdb.DuckDBPyConnection, k: int = 12
) -> dict[str, list[dict]]:
    """For every SKU, return up to ``k`` candidate substitute rows in the
    same category. We keep all candidates from the same category in
    memory once and slice per-SKU at render time — far cheaper than
    one randomized query per SKU."""
    rows = conn.execute(
        "SELECT id, name, manufacturer, sub_type, category FROM skus"
    ).fetchall()
    by_category: dict[str, list[dict]] = {}
    for sid, name, mfr, sub, cat in rows:
        by_category.setdefault(cat, []).append(
            {"id": sid, "name": name, "manufacturer": mfr, "sub_type": sub}
        )
    return by_category


def _candidates_for(sku: dict, by_category: dict[str, list[dict]], k: int = 12) -> list[dict]:
    pool = [c for c in by_category.get(sku["category"], []) if c["id"] != sku["id"]]
    # Same sub-type first, then different-manufacturer, then any remaining; cap at k.
    pool.sort(
        key=lambda c: (
            0 if c["sub_type"] == sku["sub_type"] else 1,
            0 if c["manufacturer"] != sku["manufacturer"] else 1,
        )
    )
    return pool[:k]


def generate_all(
    conn: duckdb.DuckDBPyConnection,
    wiki_dir: Path,
    enricher: Enricher | None = None,
    enrich_limit: int | None = None,
) -> int:
    """Generate every SKU page.

    If ``enricher`` is given, the first ``enrich_limit`` SKUs (or all of
    them if ``enrich_limit`` is None) get LLM-written narrative.
    Remaining SKUs use the deterministic template fallback.
    """
    out_dir = wiki_dir / "skus"
    out_dir.mkdir(parents=True, exist_ok=True)

    skus = conn.execute("SELECT * FROM skus").fetchdf().to_dict("records")
    suppliers = {
        r["id"]: r["name"]
        for r in conn.execute("SELECT id, name FROM suppliers").fetchdf().to_dict("records")
    }
    inventory_by_sku = _prefetch_inventory(conn)
    top_customers_by_sku = _prefetch_top_customers(conn, k=5)
    candidates_by_category = _prefetch_substitute_candidates(conn)

    count = 0
    enriched = 0
    for idx, sku in enumerate(tqdm(skus, desc="SKU pages", unit="page")):
        inventory = inventory_by_sku.get(sku["id"], [])
        top_customers = top_customers_by_sku.get(sku["id"], [])

        narrative: Narrative | None = None
        if enricher and (enrich_limit is None or idx < enrich_limit):
            candidates = _candidates_for(sku, candidates_by_category)
            try:
                narrative = enricher(sku, candidates)
                if narrative is not None:
                    enriched += 1
            except Exception:  # never block the pipeline on a single bad call
                narrative = None

        page = _render_sku_page(
            sku, suppliers.get(sku["primary_supplier_id"], "?"),
            inventory, top_customers, narrative=narrative,
        )
        (out_dir / f"{sku['id']}.md").write_text(page, encoding="utf-8")
        count += 1

    if enricher:
        print(f"  enriched {enriched}/{count} SKU pages with LLM narrative")
    return count
