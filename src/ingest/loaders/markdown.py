"""Markdown loader.

For internal SOPs, synthesized regulatory summaries, manufacturer TSBs,
and the synthetic install manual. Strips YAML frontmatter (it's already
in the manifest entry) and emits one Document per file.

Headings are not pre-parsed here — the chunker handles structural splits
directly on the markdown source.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from src.ingest.loaders.base import Document

_FRONTMATTER_RE = re.compile(r"^---\n.*?\n---\n", re.DOTALL)


def load(path: Path, source_id: str, manifest_entry: dict[str, Any]) -> list[Document]:
    raw = path.read_text(encoding="utf-8")
    body = _FRONTMATTER_RE.sub("", raw, count=1).lstrip("\n")
    metadata = {
        "source_path": str(path),
        "source_type": "markdown",
        "bucket": manifest_entry.get("bucket"),
        "title": manifest_entry.get("title"),
        "issuer": manifest_entry.get("issuer"),
        "doc_date": manifest_entry.get("doc_date"),
        "license": manifest_entry.get("license"),
    }
    for k in ("manufacturer", "refrigerants", "regulations"):
        if k in manifest_entry:
            metadata[k] = manifest_entry[k]
    return [Document(source_id=source_id, content=body, metadata=metadata)]
