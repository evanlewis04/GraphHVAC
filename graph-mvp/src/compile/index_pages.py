"""Generate the top-level _index.md and per-category index pages so the
Obsidian vault has clean entry points and the agent has easy starting
nodes for ``list_wiki_directory`` traversal.

Also generates concept pages — cross-cutting analyses (e.g.,
"R-410A phase-out exposure", "Lennox tariff impact") — by asking the
LLM to synthesize across the entity pages.
"""

from __future__ import annotations

from pathlib import Path

import duckdb


def generate_indexes(wiki_dir: Path) -> None:
    raise NotImplementedError


def generate_concept_pages(conn: duckdb.DuckDBPyConnection, wiki_dir: Path) -> None:
    raise NotImplementedError
