"""Write path for retrieval.

Persists ``Chunk`` records (with embeddings + metadata) to LanceDB and
rebuilds an in-process BM25 index over the same chunks. Both stores live
under ``data/`` by default.

LanceDB is chosen for embedded operation (no server), fast local-SSD
performance, and native support for filters on metadata columns. BM25
is built via ``rank_bm25`` and pickled to disk for fast cold-start.

The store is **whole-source idempotent**: when chunks for a given
``source_id`` are passed in, every previously-indexed chunk for that
source is removed first, then the new set written. This guarantees that
re-ingesting a changed source doesn't leave orphan chunks.
"""

from __future__ import annotations

import json
import os
import pickle
import shutil
from pathlib import Path
from typing import Any, Sequence

import lancedb
import pyarrow as pa
from rank_bm25 import BM25Okapi

from src.ingest.chunking import Chunk

DEFAULT_LANCEDB_PATH = Path(os.environ.get("GRAPH_DATA_DIR", "./data")) / "retrieval.lancedb"
DEFAULT_BM25_PATH = Path(os.environ.get("GRAPH_DATA_DIR", "./data")) / "bm25.pkl"
TABLE_NAME = "chunks"
EMBED_DIM = 1024


def _schema() -> pa.Schema:
    return pa.schema([
        pa.field("chunk_id", pa.string()),
        pa.field("source_id", pa.string()),
        pa.field("ordinal", pa.int32()),
        pa.field("content", pa.string()),
        pa.field("heading_path", pa.list_(pa.string())),
        pa.field("page_start", pa.int32()),
        pa.field("page_end", pa.int32()),
        pa.field("char_start", pa.int32()),
        pa.field("char_end", pa.int32()),
        pa.field("metadata_json", pa.string()),
        # Filterable columns lifted out of metadata for fast WHERE clauses.
        pa.field("bucket", pa.string()),
        pa.field("source_type", pa.string()),
        pa.field("manufacturer", pa.string()),
        pa.field("vector", pa.list_(pa.float32(), EMBED_DIM)),
    ])


def _to_row(chunk: Chunk, embedding: list[float]) -> dict[str, Any]:
    page_start = chunk.page_range[0] if chunk.page_range else -1
    page_end = chunk.page_range[1] if chunk.page_range else -1
    char_start = chunk.char_range[0] if chunk.char_range else -1
    char_end = chunk.char_range[1] if chunk.char_range else -1
    # First-class manufacturer/source_type columns for filtering speed.
    manufacturer = ""
    if isinstance(chunk.metadata.get("manufacturer"), str):
        manufacturer = chunk.metadata["manufacturer"]
    elif chunk.metadata.get("mentioned_manufacturers"):
        manufacturer = ", ".join(chunk.metadata["mentioned_manufacturers"])
    return {
        "chunk_id": chunk.chunk_id,
        "source_id": chunk.source_id,
        "ordinal": chunk.ordinal,
        "content": chunk.content,
        "heading_path": chunk.heading_path or [],
        "page_start": page_start,
        "page_end": page_end,
        "char_start": char_start,
        "char_end": char_end,
        "metadata_json": json.dumps(chunk.metadata, default=str),
        "bucket": str(chunk.metadata.get("bucket") or ""),
        "source_type": str(chunk.metadata.get("source_type") or ""),
        "manufacturer": manufacturer,
        "vector": [float(x) for x in embedding],
    }


def _open_table(lancedb_path: Path):
    lancedb_path.mkdir(parents=True, exist_ok=True)
    db = lancedb.connect(str(lancedb_path))
    if TABLE_NAME in db.table_names():
        return db, db.open_table(TABLE_NAME)
    table = db.create_table(TABLE_NAME, schema=_schema())
    return db, table


def _rebuild_bm25(bm25_path: Path, *, lancedb_path: Path) -> int:
    """Pull every chunk from LanceDB and rebuild the BM25 index."""
    db = lancedb.connect(str(lancedb_path))
    if TABLE_NAME not in db.table_names():
        if bm25_path.exists():
            bm25_path.unlink()
        return 0
    table = db.open_table(TABLE_NAME)
    rows = table.to_arrow().to_pylist()
    if not rows:
        if bm25_path.exists():
            bm25_path.unlink()
        return 0
    corpus_ids = [r["chunk_id"] for r in rows]
    tokenized = [_tokenize(r["content"]) for r in rows]
    bm25 = BM25Okapi(tokenized)
    bm25_path.parent.mkdir(parents=True, exist_ok=True)
    with bm25_path.open("wb") as f:
        pickle.dump({"bm25": bm25, "chunk_ids": corpus_ids}, f)
    return len(rows)


def _tokenize(text: str) -> list[str]:
    """Cheap tokenizer for BM25 — lowercased word characters."""
    import re
    return re.findall(r"\w+", text.lower())


def index_chunks(
    chunks: Sequence[Chunk],
    embeddings: Sequence[list[float]],
    *,
    lancedb_path: Path | None = None,
    bm25_path: Path | None = None,
) -> dict[str, int]:
    """Upsert chunks into LanceDB and rebuild BM25.

    Idempotent at the source-id level: for every distinct ``source_id``
    in ``chunks``, all existing rows with that source_id are deleted
    before the new chunks are inserted. This ensures re-ingesting a
    changed source doesn't leave orphan chunks behind.

    Returns counts: ``{inserted, deleted, sources_touched}``.
    """
    if len(chunks) != len(embeddings):
        raise ValueError(f"chunks ({len(chunks)}) and embeddings ({len(embeddings)}) length mismatch")

    lancedb_path = lancedb_path or DEFAULT_LANCEDB_PATH
    bm25_path = bm25_path or DEFAULT_BM25_PATH

    db, table = _open_table(lancedb_path)

    source_ids = sorted({c.source_id for c in chunks})
    deleted = 0
    for sid in source_ids:
        # Count before deleting for reporting.
        existing = table.search().where(
            f"source_id = '{sid}'", prefilter=True,
        ).limit(10000).to_arrow().num_rows
        if existing:
            table.delete(f"source_id = '{sid}'")
            deleted += existing

    rows = [_to_row(c, e) for c, e in zip(chunks, embeddings)]
    if rows:
        table.add(rows)

    bm25_count = _rebuild_bm25(bm25_path, lancedb_path=lancedb_path)

    return {
        "inserted": len(rows),
        "deleted": deleted,
        "sources_touched": len(source_ids),
        "bm25_corpus_size": bm25_count,
    }


def drop_index(
    *,
    lancedb_path: Path | None = None,
    bm25_path: Path | None = None,
) -> None:
    """Delete the LanceDB store and BM25 index. Used by tests and reset scripts."""
    lancedb_path = lancedb_path or DEFAULT_LANCEDB_PATH
    bm25_path = bm25_path or DEFAULT_BM25_PATH
    if lancedb_path.exists():
        shutil.rmtree(lancedb_path)
    if bm25_path.exists():
        bm25_path.unlink()


def index_stats(*, lancedb_path: Path | None = None) -> dict[str, Any]:
    """Quick stats for the Ingest UI / debugging."""
    lancedb_path = lancedb_path or DEFAULT_LANCEDB_PATH
    if not lancedb_path.exists():
        return {"exists": False, "chunks": 0, "sources": 0}
    db = lancedb.connect(str(lancedb_path))
    if TABLE_NAME not in db.table_names():
        return {"exists": False, "chunks": 0, "sources": 0}
    table = db.open_table(TABLE_NAME)
    rows = table.to_arrow().to_pylist()
    sources = {r["source_id"].split("#", 1)[0] for r in rows}
    return {"exists": True, "chunks": len(rows), "sources": len(sources)}
