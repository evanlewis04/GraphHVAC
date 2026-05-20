"""Wiki-page freshness tracking.

After an ingest run produces a new set of chunks (some added, some
updated, some removed), this module computes which wiki pages need to
rebuild based on the ``source_chunks`` lists in their frontmatter.

A page is **stale** if any of:

  - Any of its ``source_chunks`` ids no longer exists in the LanceDB
    index (chunk was removed or its content changed; recall that
    ``chunk_id`` includes a content hash, so a changed chunk has a
    different id and the old id is gone).
  - Its ``template_version`` is below ``builder.TEMPLATE_VERSION``
    (we bumped the template; old pages need a rebuild).

``rebuild_stale()`` calls ``builder._build_one`` for every stale page
the structurer owns (i.e. pages with structurer frontmatter — the old
template-rendered SKU/supplier/customer pages without
``source_chunks`` are ignored).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import lancedb

from src.retrieval.index import DEFAULT_LANCEDB_PATH, TABLE_NAME
from src.structure.builder import (
    NEW_ENTITY_TYPES,
    TEMPLATE_VERSION,
    BuildResult,
    _build_one,
    _enumerate_instances,
    _load_concepts,
    iter_structurer_pages,
)


@dataclass(frozen=True)
class StalePage:
    wiki_path: Path
    entity_type: str
    entity_id: str
    reason: str  # "chunk_removed" | "template_upgrade"
    missing_chunks: list[str]


def _current_chunk_ids(lancedb_path: Path | None = None) -> set[str]:
    path = lancedb_path or DEFAULT_LANCEDB_PATH
    if not path.exists():
        return set()
    db = lancedb.connect(str(path))
    if TABLE_NAME not in db.table_names():
        return set()
    rows = db.open_table(TABLE_NAME).to_arrow().to_pylist()
    return {r["chunk_id"] for r in rows}


def scan_stale(wiki_dir: Path | None = None) -> list[StalePage]:
    """Return the list of structurer-built pages that need rebuilding."""
    chunk_ids = _current_chunk_ids()
    stale: list[StalePage] = []
    for path, fm in iter_structurer_pages(wiki_dir):
        if int(fm.get("template_version", 0)) < TEMPLATE_VERSION:
            stale.append(StalePage(
                wiki_path=path,
                entity_type=fm.get("entity_type", "?"),
                entity_id=str(fm.get("entity_id", "?")),
                reason="template_upgrade",
                missing_chunks=[],
            ))
            continue
        page_chunks = list(fm.get("source_chunks") or [])
        missing = [c for c in page_chunks if c not in chunk_ids]
        if missing:
            stale.append(StalePage(
                wiki_path=path,
                entity_type=fm.get("entity_type", "?"),
                entity_id=str(fm.get("entity_id", "?")),
                reason="chunk_removed",
                missing_chunks=missing,
            ))
    return stale


def rebuild_stale(
    *,
    use_llm: bool = True,
    force: bool = False,
    on_progress=None,
) -> list[BuildResult]:
    """Rebuild every stale structurer-owned page."""
    concepts = _load_concepts()
    stale = scan_stale()
    results: list[BuildResult] = []
    for s in stale:
        if s.entity_type not in concepts:
            results.append(BuildResult(
                entity_type=s.entity_type,
                entity_id=s.entity_id,
                wiki_path=s.wiki_path,
                skipped_reason="entity_type not in concepts.yaml",
            ))
            continue
        concept = concepts[s.entity_type]
        instances = _enumerate_instances(concept)
        match = next((i for i in instances if str(i["value"]) == s.entity_id), None)
        if match is None:
            results.append(BuildResult(
                entity_type=s.entity_type,
                entity_id=s.entity_id,
                wiki_path=s.wiki_path,
                skipped_reason="instance disappeared from source query",
            ))
            continue
        try:
            result = _build_one(s.entity_type, match, concept, use_llm=use_llm, force=force)
        except Exception as exc:
            result = BuildResult(
                entity_type=s.entity_type,
                entity_id=s.entity_id,
                wiki_path=s.wiki_path,
                skipped_reason=f"{type(exc).__name__}: {exc}",
            )
        results.append(result)
        if on_progress:
            on_progress(result)
    return results


def stats(wiki_dir: Path | None = None) -> dict:
    """Summary stats for the Knowledge-health UI / debugging."""
    total = 0
    by_type: dict[str, int] = {}
    by_synth: dict[str, int] = {}
    for _path, fm in iter_structurer_pages(wiki_dir):
        total += 1
        et = fm.get("entity_type", "?")
        by_type[et] = by_type.get(et, 0) + 1
        s = fm.get("synthesizer", "?")
        by_synth[s] = by_synth.get(s, 0) + 1
    new_types_built = sum(by_type.get(t, 0) for t in NEW_ENTITY_TYPES)
    return {
        "structurer_pages": total,
        "by_entity_type": by_type,
        "by_synthesizer": by_synth,
        "new_entity_types_built": new_types_built,
        "template_version": TEMPLATE_VERSION,
    }
