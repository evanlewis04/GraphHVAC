"""Service-ticket loader.

Synthetic service tickets / contractor notes stored as JSONL (one ticket
per line). Each ticket becomes one ``Document``. Required fields per
record: ``ticket_id``, ``customer_id``, ``date``, ``equipment_model``,
``notes``. Optional: ``fault_code``, ``parts_used``, ``technician``,
``warehouse``, ``manufacturer``.

Each Document's ``source_id`` is suffixed with ``#<ticket_id>`` so the
ticket is uniquely citable.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.ingest.loaders.base import Document


def _render(record: dict[str, Any]) -> str:
    """Compact human-readable rendering for retrieval."""
    head = (
        f"Ticket {record.get('ticket_id', '?')} "
        f"({record.get('date', '?')}, customer {record.get('customer_id', '?')})"
    )
    extras = []
    for k in ("manufacturer", "equipment_model", "warehouse", "fault_code", "parts_used"):
        if record.get(k):
            extras.append(f"{k}: {record[k]}")
    extras_line = " | ".join(extras)
    notes = record.get("notes", "").strip()
    return f"{head}\n{extras_line}\n\nNotes: {notes}".strip()


def load(path: Path, source_id: str, manifest_entry: dict[str, Any]) -> list[Document]:
    docs: list[Document] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        record = json.loads(line)
        ticket_id = record.get("ticket_id", f"row-{len(docs)+1:03d}")
        metadata = {
            "source_path": str(path),
            "source_type": "ticket",
            "bucket": manifest_entry.get("bucket"),
            "title": manifest_entry.get("title"),
            "issuer": manifest_entry.get("issuer"),
            "doc_date": record.get("date") or manifest_entry.get("doc_date"),
            "license": manifest_entry.get("license"),
            "ticket_id": ticket_id,
            "customer_id": record.get("customer_id"),
            "manufacturer": record.get("manufacturer"),
            "equipment_model": record.get("equipment_model"),
            "warehouse": record.get("warehouse"),
            "fault_code": record.get("fault_code"),
            "parts_used": record.get("parts_used"),
        }
        metadata = {k: v for k, v in metadata.items() if v is not None}
        docs.append(Document(
            source_id=f"{source_id}#{ticket_id}",
            content=_render(record),
            metadata=metadata,
        ))
    return docs
