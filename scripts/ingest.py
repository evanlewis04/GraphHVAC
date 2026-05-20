"""Ingest driver.

Reads ``data/sources/manifest.yaml``, walks every declared source,
runs the loader → chunker → metadata-enrichment → embedder →
indexer pipeline, and audit-logs the run.

Idempotent: re-running with no source changes is cheap (embeddings
hit the content-hash cache; LanceDB upserts at source-id granularity).

Usage:
    python scripts/ingest.py
    python scripts/ingest.py --manifest data/sources/manifest.yaml
    python scripts/ingest.py --only bulletin-epa-aim-act-summary
    python scripts/ingest.py --llm-enrich      # opt-in Haiku metadata pass
    python scripts/ingest.py --drop-first      # wipe LanceDB before ingest
    python scripts/ingest.py --skip-anchors    # skip reference-only entries
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path
from typing import Any

import yaml

from src.audit.logger import log_step, new_trace_id
from src.ingest.chunking import chunk_document
from src.ingest.embed import embed_chunks
from src.ingest.loaders.base import load_for_entry
from src.ingest.metadata import enrich_chunks
from src.retrieval.index import drop_index, index_chunks, index_stats

ROOT = Path(__file__).resolve().parents[1]
SOURCES_DIR = ROOT / "data" / "sources"


def _load_manifest(path: Path) -> list[dict[str, Any]]:
    manifest = yaml.safe_load(path.read_text(encoding="utf-8"))
    return manifest["sources"]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=SOURCES_DIR / "manifest.yaml")
    parser.add_argument(
        "--only", action="append", default=None,
        help="Only ingest the named source_id(s). Repeatable.",
    )
    parser.add_argument("--llm-enrich", action="store_true",
                        help="Opt into Haiku-driven metadata enrichment.")
    parser.add_argument("--drop-first", action="store_true",
                        help="Drop the LanceDB index before ingest (full rebuild).")
    parser.add_argument("--skip-anchors", action="store_true",
                        help="Skip entries with license: reference-only.")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    if args.drop_first:
        drop_index()

    entries = _load_manifest(args.manifest)
    if args.only:
        wanted = set(args.only)
        entries = [e for e in entries if e["source_id"] in wanted]
        if not entries:
            print(f"No manifest entries match --only={args.only}", file=sys.stderr)
            sys.exit(1)

    trace_id = new_trace_id()
    log_step(trace_id, 0, "ingest_started", {
        "manifest": str(args.manifest),
        "entry_count": len(entries),
        "llm_enrich": args.llm_enrich,
    })

    t0 = time.time()
    totals = {
        "sources_processed": 0,
        "sources_skipped": 0,
        "documents": 0,
        "chunks_indexed": 0,
        "chunks_deleted": 0,
    }

    for i, entry in enumerate(entries, start=1):
        sid = entry["source_id"]
        if args.skip_anchors and entry.get("license") == "reference-only":
            totals["sources_skipped"] += 1
            if not args.quiet:
                print(f"[skip] {sid} (reference-only)")
            continue

        try:
            docs = load_for_entry(entry, SOURCES_DIR)
        except FileNotFoundError as exc:
            totals["sources_skipped"] += 1
            log_step(trace_id, i, "source_missing", {"source_id": sid, "error": str(exc)})
            if not args.quiet:
                print(f"[skip] {sid} (file missing)")
            continue
        except Exception as exc:
            log_step(trace_id, i, "load_error", {
                "source_id": sid, "error": f"{type(exc).__name__}: {exc}",
            })
            if not args.quiet:
                print(f"[ERROR load] {sid}: {exc}")
            continue

        if not docs:
            totals["sources_skipped"] += 1
            log_step(trace_id, i, "source_empty", {"source_id": sid})
            continue

        # Chunk every Document this source produced.
        all_chunks = []
        for doc in docs:
            all_chunks.extend(chunk_document(doc))
        if not all_chunks:
            totals["sources_skipped"] += 1
            log_step(trace_id, i, "no_chunks", {"source_id": sid, "docs": len(docs)})
            continue

        # Metadata enrichment (pattern always; LLM optional).
        all_chunks = enrich_chunks(all_chunks, use_llm=args.llm_enrich)

        # Embed.
        embeddings = embed_chunks(all_chunks)

        # Index.
        result = index_chunks(all_chunks, embeddings)

        totals["sources_processed"] += 1
        totals["documents"] += len(docs)
        totals["chunks_indexed"] += result["inserted"]
        totals["chunks_deleted"] += result["deleted"]

        log_step(trace_id, i, "source_indexed", {
            "source_id": sid,
            "docs": len(docs),
            "chunks": result["inserted"],
            "deleted": result["deleted"],
        })
        if not args.quiet:
            print(
                f"[{i:3d}/{len(entries)}] {sid}: "
                f"{len(docs)} docs -> {result['inserted']} chunks "
                f"({result['deleted']} replaced)"
            )

    elapsed = time.time() - t0
    stats = index_stats()
    log_step(trace_id, len(entries) + 1, "ingest_complete", {
        "elapsed_seconds": round(elapsed, 2),
        **totals,
        "index_chunks": stats["chunks"],
        "index_sources": stats["sources"],
    })

    print()
    print(f"Ingest complete in {elapsed:.1f}s")
    print(f"  sources processed:  {totals['sources_processed']}")
    print(f"  sources skipped:    {totals['sources_skipped']}")
    print(f"  documents loaded:   {totals['documents']}")
    print(f"  chunks indexed:     {totals['chunks_indexed']}")
    print(f"  chunks replaced:    {totals['chunks_deleted']}")
    print(f"  index totals:       {stats['chunks']} chunks across {stats['sources']} sources")
    print(f"  trace_id:           {trace_id}")


if __name__ == "__main__":
    main()
