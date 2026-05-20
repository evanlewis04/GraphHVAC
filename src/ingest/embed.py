"""Embedding generation with a content-hash cache.

Primary path: Voyage embeddings (``voyage-3`` by default, configurable
via ``GRAPH_EMBED_MODEL``). Requires ``VOYAGE_API_KEY`` in the env
and the optional ``voyageai`` package installed
(``pip install -e .[voyage]``).

Fallback: when no Voyage key is available, returns deterministic
hash-derived pseudo-vectors. These are NOT semantically meaningful —
they exist so the LanceDB schema stays consistent and a reviewer can
clone-and-run the project without a Voyage account. With the fallback,
hybrid retrieval degrades to BM25-only behaviour. A loud warning is
printed once per process.

Cache: SQLite at ``data/embed_cache.sqlite``, keyed by
``(model, sha256(content))``. Re-embedding is free until content
changes.
"""

from __future__ import annotations

import hashlib
import os
import pickle
import sqlite3
import sys
import threading
from pathlib import Path
from typing import Sequence

from src.ingest.chunking import Chunk

DEFAULT_MODEL = os.environ.get("GRAPH_EMBED_MODEL", "voyage-3")
EMBED_DIM = 1024  # voyage-3 dimension; fallback matches for schema compat
DEFAULT_CACHE_PATH = Path(os.environ.get("GRAPH_DATA_DIR", "./data")) / "embed_cache.sqlite"
_BATCH_SIZE = 64

_fallback_warned = False
_lock = threading.Lock()


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _open_cache(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.execute(
        "CREATE TABLE IF NOT EXISTS embeddings ("
        "model TEXT NOT NULL, content_hash TEXT NOT NULL, vector BLOB NOT NULL, "
        "PRIMARY KEY (model, content_hash))"
    )
    return conn


def _cache_get(conn: sqlite3.Connection, model: str, h: str) -> list[float] | None:
    row = conn.execute(
        "SELECT vector FROM embeddings WHERE model = ? AND content_hash = ?",
        (model, h),
    ).fetchone()
    return pickle.loads(row[0]) if row else None


def _cache_put(conn: sqlite3.Connection, model: str, h: str, vec: list[float]) -> None:
    conn.execute(
        "INSERT OR REPLACE INTO embeddings (model, content_hash, vector) VALUES (?, ?, ?)",
        (model, h, pickle.dumps(vec)),
    )


def _voyage_available() -> bool:
    if not os.environ.get("VOYAGE_API_KEY"):
        return False
    try:
        import voyageai  # noqa: F401
        return True
    except ImportError:
        return False


def _warn_fallback_once() -> None:
    global _fallback_warned
    with _lock:
        if _fallback_warned:
            return
        print(
            "[embed] WARNING: VOYAGE_API_KEY not set (or voyageai not installed). "
            "Falling back to deterministic hash pseudo-embeddings. Hybrid retrieval "
            "will behave like BM25-only. Install with: pip install -e .[voyage] and "
            "set VOYAGE_API_KEY in .env to enable real embeddings.",
            file=sys.stderr,
        )
        _fallback_warned = True


def _hash_pseudo_vector(text: str, dim: int = EMBED_DIM) -> list[float]:
    """Deterministic per-content vector. Not semantic."""
    digest = hashlib.sha256(text.encode("utf-8")).digest()
    floats: list[float] = []
    while len(floats) < dim:
        digest = hashlib.sha256(digest).digest()
        for b in digest:
            floats.append((b - 128) / 128.0)
            if len(floats) >= dim:
                break
    # L2-normalize so cosine works.
    norm = sum(x * x for x in floats) ** 0.5 or 1.0
    return [x / norm for x in floats]


def _voyage_embed(texts: list[str], model: str) -> list[list[float]]:
    import voyageai
    client = voyageai.Client(api_key=os.environ["VOYAGE_API_KEY"])
    # input_type="document" for the corpus side, "query" for queries
    result = client.embed(texts=texts, model=model, input_type="document")
    return [list(v) for v in result.embeddings]


def embed_chunks(
    chunks: Sequence[Chunk],
    *,
    model: str | None = None,
    cache_path: Path | None = None,
) -> list[list[float]]:
    """Return one embedding vector per chunk, in input order."""
    if not chunks:
        return []
    model = model or DEFAULT_MODEL
    cache_path = cache_path or DEFAULT_CACHE_PATH

    use_voyage = _voyage_available()
    if not use_voyage:
        _warn_fallback_once()

    conn = _open_cache(cache_path)
    try:
        hashes = [_sha(c.content) for c in chunks]
        cached = [_cache_get(conn, model, h) for h in hashes]
        miss_idx = [i for i, v in enumerate(cached) if v is None]

        if miss_idx:
            miss_texts = [chunks[i].content for i in miss_idx]
            if use_voyage:
                miss_vecs: list[list[float]] = []
                for batch_start in range(0, len(miss_texts), _BATCH_SIZE):
                    batch = miss_texts[batch_start : batch_start + _BATCH_SIZE]
                    miss_vecs.extend(_voyage_embed(batch, model))
            else:
                miss_vecs = [_hash_pseudo_vector(t) for t in miss_texts]

            for i, vec in zip(miss_idx, miss_vecs):
                cached[i] = vec
                _cache_put(conn, model, hashes[i], vec)
            conn.commit()

        # mypy: cached now has no Nones
        return [v for v in cached if v is not None]
    finally:
        conn.close()


def embed_query(query: str, *, model: str | None = None) -> list[float]:
    """Embed a single query string for retrieval.

    Queries are not cached. With the fallback path, returns a pseudo-vector
    that won't match anything meaningful — callers should rely on BM25.
    """
    model = model or DEFAULT_MODEL
    if not _voyage_available():
        _warn_fallback_once()
        return _hash_pseudo_vector(query)
    import voyageai
    client = voyageai.Client(api_key=os.environ["VOYAGE_API_KEY"])
    result = client.embed(texts=[query], model=model, input_type="query")
    return list(result.embeddings[0])
