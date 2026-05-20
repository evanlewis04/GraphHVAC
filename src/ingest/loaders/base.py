"""Shared loader protocol, the normalized ``Document`` dataclass, and dispatch.

Every per-format loader (``pdf.py``, ``markdown.py``, ``email.py``,
``ticket.py``, ``csv.py``) returns a list of ``Document`` instances.
The chunker downstream operates only on ``Document`` — it never sees
the raw source format.

``load_for_entry(manifest_entry, sources_root)`` is the dispatcher
used by the ingest driver; it looks at the entry's ``type`` field
and calls the corresponding loader.
"""

from __future__ import annotations

import importlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol


@dataclass(frozen=True)
class Document:
    """A normalized source document ready for chunking.

    Attributes
    ----------
    source_id:
        Stable identifier from ``manifest.yaml``. For loaders that emit
        multiple Documents per file (tickets), suffix the manifest
        ``source_id`` with ``#<n>`` so each Document remains uniquely
        addressable.
    content:
        Plain-text body ready for chunking. Loaders strip format-specific
        noise (frontmatter, control characters).
    metadata:
        Required keys: ``source_path``, ``source_type``, ``bucket``.
        Optional per loader: ``page_offsets``, ``headings``, ``date``,
        ``manufacturer``, ``thread_id``, ``sender``, ``license``,
        ``record_id`` (tickets), ``page_count`` (PDF).
    """

    source_id: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)


class Loader(Protocol):
    """Protocol every per-format loader satisfies."""

    def load(self, path: Path, source_id: str, manifest_entry: dict[str, Any]) -> list[Document]:
        ...


# Loader-name → import path. Kept explicit so dispatch is easy to read
# and adding a new loader is a one-line change.
_LOADER_MODULES = {
    "markdown": "src.ingest.loaders.markdown",
    "email": "src.ingest.loaders.email",
    "ticket": "src.ingest.loaders.ticket",
    "csv": "src.ingest.loaders.csv",
    "pdf": "src.ingest.loaders.pdf",
}


def load_for_entry(manifest_entry: dict[str, Any], sources_root: Path) -> list[Document]:
    """Dispatch a manifest entry to the right loader and return Documents."""
    type_ = manifest_entry["type"]
    if type_ not in _LOADER_MODULES:
        raise ValueError(f"Unknown source type {type_!r} for {manifest_entry['source_id']}")

    path = sources_root / manifest_entry["path"]
    if not path.exists():
        # Reference-only sources may legitimately be absent (fetcher not run).
        if manifest_entry.get("license") == "reference-only":
            return []
        raise FileNotFoundError(f"{path} (source_id={manifest_entry['source_id']})")

    mod = importlib.import_module(_LOADER_MODULES[type_])
    return mod.load(path, manifest_entry["source_id"], manifest_entry)
