"""CSV loader for retrieval-side documents.

Distinct from ``src/ingest/csv_loader.py``, which loads ERP CSVs into
DuckDB. This loader is for *retrieval* — turning spec sheets / price
books into a Document the agent can cite.

For Phase 3 the spec CSVs are small (15–35 rows each) so we emit one
Document per file with rows rendered as a markdown table. The chunker
will split the table by section if it overflows token budgets.

Larger files in the future can declare ``group_by: <column>`` in
``loader_options`` and we'll emit one Document per group.
"""

from __future__ import annotations

import csv as _csv
from pathlib import Path
from typing import Any

from src.ingest.loaders.base import Document


def _render_table(rows: list[list[str]]) -> str:
    if not rows:
        return ""
    header, *body = rows
    out = ["| " + " | ".join(header) + " |"]
    out.append("|" + "|".join(["---"] * len(header)) + "|")
    for row in body:
        out.append("| " + " | ".join(row) + " |")
    return "\n".join(out)


def load(path: Path, source_id: str, manifest_entry: dict[str, Any]) -> list[Document]:
    with path.open("r", encoding="utf-8") as f:
        rows = list(_csv.reader(f))

    title = manifest_entry.get("title", path.stem)
    issuer = manifest_entry.get("issuer", "")
    category = manifest_entry.get("category", "")
    manufacturer = manifest_entry.get("manufacturer", "")
    header_md = f"# {title}\n"
    sub_bits = [b for b in (issuer, manufacturer, category) if b]
    if sub_bits:
        header_md += "_" + " · ".join(sub_bits) + "_\n\n"
    table_md = _render_table(rows)
    content = header_md + "\n" + table_md

    metadata = {
        "source_path": str(path),
        "source_type": "csv",
        "bucket": manifest_entry.get("bucket"),
        "title": title,
        "issuer": issuer or None,
        "manufacturer": manufacturer or None,
        "category": category or None,
        "doc_date": manifest_entry.get("doc_date"),
        "license": manifest_entry.get("license"),
        "row_count": max(0, len(rows) - 1),
    }
    metadata = {k: v for k, v in metadata.items() if v is not None}
    return [Document(source_id=source_id, content=content, metadata=metadata)]
