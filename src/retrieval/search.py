"""Read path for retrieval.

``retrieve(query, k, filters)`` returns top-k ranked chunks combining:

  1. Lexical (BM25 over the chunk corpus)
  2. Semantic (cosine on embeddings stored in LanceDB)

Scores are min-max normalized per channel and combined as
``alpha * vector + (1 - alpha) * bm25`` (default ``alpha = 0.6``).
Optional Voyage ``rerank-2`` is applied to the top-``rerank_pool``
(default 25) and the final top-``k`` is returned. Reranking is
skipped automatically when ``VOYAGE_API_KEY`` is not set.

Filters supported:
  - ``bucket`` (str) — manifest bucket name
  - ``source_type`` (str) — markdown / email / pdf / ticket / csv
  - ``manufacturer`` (str) — case-insensitive substring match
  - ``source_id`` (str) — exact match (also catches per-message/ticket suffixes)
  - ``refrigerant`` (str) — looked up in ``mentioned_refrigerants`` metadata
  - ``date_from``, ``date_to`` (str ISO) — checks ``doc_date`` in metadata

Filters using first-class columns are pushed down to LanceDB; metadata
filters are applied post-fetch in Python.
"""

from __future__ import annotations

import json
import math
import os
import pickle
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

import lancedb
import yaml
from rank_bm25 import BM25Okapi

from src.ingest.embed import embed_query
from src.retrieval.index import (
    DEFAULT_BM25_PATH,
    DEFAULT_LANCEDB_PATH,
    TABLE_NAME,
)

SOURCES_DIR = Path(os.environ.get("GRAPH_DATA_DIR", "./data")) / "sources"
_MANIFEST_PATH = SOURCES_DIR / "manifest.yaml"
_VECTOR_DIM = 1024


@dataclass(frozen=True)
class RetrievedChunk:
    """A retrieval hit ready to feed the agent's ``retrieve`` tool result.

    ``citation_id`` is allocated by the tool wrapper (per-trace), not by
    ``retrieve()`` itself — search returns an empty string and the caller
    fills it in from the per-trace registry.
    """

    citation_id: str
    chunk_id: str
    source_id: str
    snippet: str
    score: float
    bm25_score: float
    vector_score: float
    rerank_score: float | None
    heading_path: list[str]
    page_range: tuple[int, int] | None
    metadata: dict[str, Any]


# ---------------------------------------------------------------------------
# Index access
# ---------------------------------------------------------------------------


def _tokenize(text: str) -> list[str]:
    return re.findall(r"\w+", text.lower())


@lru_cache(maxsize=1)
def _load_bm25(path_str: str) -> tuple[BM25Okapi, list[str]] | tuple[None, None]:
    path = Path(path_str)
    if not path.exists():
        return None, None
    with path.open("rb") as f:
        payload = pickle.load(f)
    return payload["bm25"], payload["chunk_ids"]


@lru_cache(maxsize=1)
def _load_chunks(lancedb_path_str: str) -> dict[str, dict[str, Any]]:
    path = Path(lancedb_path_str)
    if not path.exists():
        return {}
    db = lancedb.connect(str(path))
    if TABLE_NAME not in db.table_names():
        return {}
    rows = db.open_table(TABLE_NAME).to_arrow().to_pylist()
    return {r["chunk_id"]: r for r in rows}


def _clear_caches() -> None:
    """Used by tests when re-indexing in the same process."""
    _load_bm25.cache_clear()
    _load_chunks.cache_clear()


# ---------------------------------------------------------------------------
# Score normalization + filters
# ---------------------------------------------------------------------------


def _minmax(scores: dict[str, float]) -> dict[str, float]:
    if not scores:
        return {}
    vals = list(scores.values())
    lo, hi = min(vals), max(vals)
    if hi - lo < 1e-9:
        return {k: 0.0 for k in scores}
    return {k: (v - lo) / (hi - lo) for k, v in scores.items()}


def _cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a)) or 1.0
    nb = math.sqrt(sum(x * x for x in b)) or 1.0
    return dot / (na * nb)


def _passes_metadata_filters(row: dict[str, Any], filters: dict[str, Any]) -> bool:
    md = json.loads(row["metadata_json"])
    refrigerant = filters.get("refrigerant")
    if refrigerant:
        mentions = md.get("mentioned_refrigerants") or md.get("refrigerants") or []
        if not any(r.lower() == refrigerant.lower() for r in mentions):
            return False
    date_from = filters.get("date_from")
    date_to = filters.get("date_to")
    if date_from or date_to:
        dd = md.get("doc_date")
        if not dd:
            return False
        if date_from and str(dd) < str(date_from):
            return False
        if date_to and str(dd) > str(date_to):
            return False
    return True


def _build_lance_where(filters: dict[str, Any]) -> str:
    """Translate first-class filters into a LanceDB WHERE clause."""
    clauses: list[str] = []
    if "bucket" in filters and filters["bucket"]:
        clauses.append(f"bucket = '{_escape(filters['bucket'])}'")
    if "source_type" in filters and filters["source_type"]:
        clauses.append(f"source_type = '{_escape(filters['source_type'])}'")
    if "manufacturer" in filters and filters["manufacturer"]:
        # case-insensitive substring via LIKE
        m = _escape(filters["manufacturer"])
        clauses.append(f"manufacturer LIKE '%{m}%'")
    if "source_id" in filters and filters["source_id"]:
        s = _escape(filters["source_id"])
        # Exact or per-message/per-record suffix.
        clauses.append(f"(source_id = '{s}' OR source_id LIKE '{s}#%')")
    return " AND ".join(clauses)


def _escape(s: str) -> str:
    return s.replace("'", "''")


# ---------------------------------------------------------------------------
# Optional Voyage rerank
# ---------------------------------------------------------------------------


def _rerank_via_voyage(query: str, candidates: list[dict[str, Any]]) -> list[float] | None:
    """Return per-candidate rerank scores, or None if Voyage unavailable."""
    if not os.environ.get("VOYAGE_API_KEY"):
        return None
    try:
        import voyageai
    except ImportError:
        return None
    client = voyageai.Client(api_key=os.environ["VOYAGE_API_KEY"])
    docs = [c["content"] for c in candidates]
    try:
        result = client.rerank(query=query, documents=docs, model="rerank-2", top_k=len(docs))
    except Exception:
        return None
    # voyageai returns a list of (index, relevance_score)
    scores = [0.0] * len(candidates)
    for r in result.results:
        scores[r.index] = float(r.relevance_score)
    return scores


# ---------------------------------------------------------------------------
# Snippets
# ---------------------------------------------------------------------------


def _snippet(content: str, query: str, max_chars: int = 280) -> str:
    """Pick a short snippet that hopefully contains query tokens."""
    qtokens = [t for t in _tokenize(query) if len(t) > 2]
    if not qtokens:
        return content[:max_chars].strip()
    lower = content.lower()
    best_pos = -1
    for tok in qtokens:
        idx = lower.find(tok)
        if idx != -1:
            best_pos = idx
            break
    if best_pos == -1:
        return content[:max_chars].strip()
    start = max(0, best_pos - 60)
    end = min(len(content), start + max_chars)
    prefix = "…" if start > 0 else ""
    suffix = "…" if end < len(content) else ""
    return prefix + content[start:end].strip() + suffix


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def retrieve(
    query: str,
    *,
    k: int = 5,
    filters: dict[str, Any] | None = None,
    alpha: float = 0.6,
    rerank: bool = True,
    rerank_pool: int = 25,
    lancedb_path: Path | None = None,
    bm25_path: Path | None = None,
) -> list[RetrievedChunk]:
    """Hybrid retrieval. Returns top-``k`` chunks ordered by combined score."""
    filters = filters or {}
    lancedb_path = lancedb_path or DEFAULT_LANCEDB_PATH
    bm25_path = bm25_path or DEFAULT_BM25_PATH

    chunks = _load_chunks(str(lancedb_path))
    if not chunks:
        return []

    bm25, bm25_ids = _load_bm25(str(bm25_path))

    # Push-down filter via LanceDB for first-class columns.
    where = _build_lance_where(filters)
    if where:
        db = lancedb.connect(str(lancedb_path))
        filtered_rows = (
            db.open_table(TABLE_NAME)
            .search()
            .where(where, prefilter=True)
            .limit(100000)
            .to_arrow()
            .to_pylist()
        )
        allowed_ids = {r["chunk_id"] for r in filtered_rows}
    else:
        allowed_ids = set(chunks.keys())

    # Apply metadata-only filters (refrigerant, date range) in Python.
    metadata_only_filters = {
        k_: v for k_, v in filters.items()
        if k_ in {"refrigerant", "date_from", "date_to"} and v
    }
    if metadata_only_filters:
        allowed_ids = {
            cid for cid in allowed_ids
            if _passes_metadata_filters(chunks[cid], metadata_only_filters)
        }

    if not allowed_ids:
        return []

    # --- BM25 over the full corpus, then filter --------------------------
    bm25_scores: dict[str, float] = {}
    if bm25 is not None and bm25_ids is not None:
        q_tokens = _tokenize(query)
        if q_tokens:
            raw = bm25.get_scores(q_tokens)
            for cid, sc in zip(bm25_ids, raw):
                if cid in allowed_ids and sc > 0:
                    bm25_scores[cid] = float(sc)

    # --- Vector cosine over the (filtered) corpus -------------------------
    q_vec = embed_query(query)
    vec_scores: dict[str, float] = {}
    for cid in allowed_ids:
        row = chunks[cid]
        v = row.get("vector")
        if v is None:
            continue
        vec_scores[cid] = _cosine(q_vec, list(v))

    # --- Combine ----------------------------------------------------------
    bm_n = _minmax(bm25_scores)
    vec_n = _minmax(vec_scores)
    combined: dict[str, float] = {}
    for cid in allowed_ids:
        combined[cid] = alpha * vec_n.get(cid, 0.0) + (1 - alpha) * bm_n.get(cid, 0.0)

    # Take top rerank_pool by combined; rerank; then truncate to k.
    pool_ids = sorted(combined, key=lambda c: combined[c], reverse=True)[:rerank_pool]
    pool_rows = [chunks[c] for c in pool_ids]

    rerank_scores: list[float] | None = None
    if rerank and pool_rows:
        rerank_scores = _rerank_via_voyage(query, pool_rows)

    if rerank_scores is not None:
        # Sort by rerank score; combined score becomes tiebreaker.
        order = sorted(
            range(len(pool_ids)),
            key=lambda i: (rerank_scores[i], combined[pool_ids[i]]),
            reverse=True,
        )
    else:
        order = list(range(len(pool_ids)))

    out: list[RetrievedChunk] = []
    for rank, i in enumerate(order[:k]):
        cid = pool_ids[i]
        row = chunks[cid]
        meta = json.loads(row["metadata_json"])
        page_range = None
        if row["page_start"] >= 0 and row["page_end"] >= 0:
            page_range = (row["page_start"], row["page_end"])
        out.append(RetrievedChunk(
            citation_id="",  # allocated by tool wrapper
            chunk_id=row["chunk_id"],
            source_id=row["source_id"],
            snippet=_snippet(row["content"], query),
            score=combined[cid],
            bm25_score=bm25_scores.get(cid, 0.0),
            vector_score=vec_scores.get(cid, 0.0),
            rerank_score=(rerank_scores[i] if rerank_scores is not None else None),
            heading_path=list(row["heading_path"] or []),
            page_range=page_range,
            metadata=meta,
        ))
    return out


# ---------------------------------------------------------------------------
# read_source — raw verification path
# ---------------------------------------------------------------------------


@lru_cache(maxsize=1)
def _manifest_index() -> dict[str, dict[str, Any]]:
    if not _MANIFEST_PATH.exists():
        return {}
    manifest = yaml.safe_load(_MANIFEST_PATH.read_text(encoding="utf-8"))
    return {e["source_id"]: e for e in manifest.get("sources", [])}


def read_source(
    source_id: str,
    *,
    max_chars: int = 8000,
    page_range: tuple[int, int] | None = None,
) -> str:
    """Return raw text from a source document.

    ``source_id`` may be the manifest id or a per-message / per-ticket
    suffix (``#msg-2``, ``#TKT-...``); the suffix is stripped to find
    the file. The full file content is returned (markdown frontmatter
    stripped), truncated to ``max_chars`` so tool results stay bounded.

    For PDFs, ``page_range`` selects which pages to include. For other
    formats it's ignored.
    """
    base_id = source_id.split("#", 1)[0]
    entries = _manifest_index()
    entry = entries.get(base_id)
    if not entry:
        return f"ERROR: unknown source_id {source_id!r}"

    path = SOURCES_DIR / entry["path"]
    if not path.exists():
        if entry.get("license") == "reference-only":
            return (
                f"[{base_id}] is a reference-only anchor; run "
                f"`python scripts/fetch_anchors.py` to download it."
            )
        return f"ERROR: file missing for {source_id!r}: {path}"

    type_ = entry["type"]
    if type_ == "markdown" or type_ == "email":
        raw = path.read_text(encoding="utf-8")
        # Strip frontmatter.
        body = re.sub(r"^---\n.*?\n---\n", "", raw, count=1, flags=re.DOTALL).lstrip("\n")
        return _truncate(body, max_chars)
    if type_ == "ticket":
        raw = path.read_text(encoding="utf-8")
        if "#" in source_id:
            wanted_id = source_id.split("#", 1)[1]
            for line in raw.splitlines():
                if line.strip() and wanted_id in line:
                    return _truncate(line, max_chars)
        return _truncate(raw, max_chars)
    if type_ == "csv":
        return _truncate(path.read_text(encoding="utf-8"), max_chars)
    if type_ == "pdf":
        # Lazy import; only used when a PDF is actually requested.
        try:
            import pymupdf
        except ImportError:
            return f"ERROR: pymupdf not installed; cannot read PDF {source_id!r}"
        doc = pymupdf.open(path)
        parts: list[str] = []
        for i, page in enumerate(doc, start=1):
            if page_range and not (page_range[0] <= i <= page_range[1]):
                continue
            parts.append(f"--- page {i} ---\n{page.get_text('text') or ''}")
        doc.close()
        return _truncate("\n\n".join(parts), max_chars)
    return f"ERROR: unsupported source type {type_!r} for {source_id!r}"


def _truncate(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + f"\n\n…[truncated; {len(text) - max_chars} more chars]"
