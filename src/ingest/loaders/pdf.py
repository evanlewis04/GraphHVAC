"""PDF loader.

Extracts text from PDFs (real public-anchor regulatory documents, plus
any future manufacturer manual PDFs). Uses PyMuPDF for speed; falls back
to pdfplumber on malformed files.

Page offsets are preserved as ``metadata['page_offsets']`` — a list of
``(page_number, char_offset)`` tuples — so the chunker can attach
``page_range`` to each chunk.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.ingest.loaders.base import Document


def _extract_with_pymupdf(path: Path) -> tuple[str, list[tuple[int, int]]]:
    import pymupdf  # local import keeps tests cheap when no PDFs are present
    doc = pymupdf.open(path)
    parts: list[str] = []
    offsets: list[tuple[int, int]] = []
    running = 0
    for i, page in enumerate(doc, start=1):
        offsets.append((i, running))
        text = page.get_text("text") or ""
        parts.append(text)
        running += len(text) + 2  # +2 for the joiner below
    doc.close()
    return "\n\n".join(parts), offsets


def _extract_with_pdfplumber(path: Path) -> tuple[str, list[tuple[int, int]]]:
    import pdfplumber
    parts: list[str] = []
    offsets: list[tuple[int, int]] = []
    running = 0
    with pdfplumber.open(path) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            offsets.append((i, running))
            text = page.extract_text() or ""
            parts.append(text)
            running += len(text) + 2
    return "\n\n".join(parts), offsets


def load(path: Path, source_id: str, manifest_entry: dict[str, Any]) -> list[Document]:
    try:
        content, offsets = _extract_with_pymupdf(path)
    except Exception:
        content, offsets = _extract_with_pdfplumber(path)

    metadata = {
        "source_path": str(path),
        "source_type": "pdf",
        "bucket": manifest_entry.get("bucket"),
        "title": manifest_entry.get("title"),
        "issuer": manifest_entry.get("issuer"),
        "doc_date": manifest_entry.get("doc_date"),
        "license": manifest_entry.get("license"),
        "page_count": len(offsets),
        "page_offsets": offsets,
    }
    for k in ("manufacturer", "refrigerants", "regulations"):
        if k in manifest_entry:
            metadata[k] = manifest_entry[k]
    metadata = {k: v for k, v in metadata.items() if v is not None}
    return [Document(source_id=source_id, content=content, metadata=metadata)]
