"""Chunk metadata enrichment.

Two paths:

1. **Deterministic pattern match** (always runs). Scans each chunk for
   known entities — manufacturers, refrigerants, regulations — using a
   curated vocabulary. Fast, free, no API. Covers the high-value cases
   because the entity universe is small and well-defined.

2. **Optional LLM enrichment** (Haiku, via ``--llm-enrich``). Picks up
   long-tail mentions and lets the model add an inferred ``doc_type``
   when the loader's bucket-derived type looks wrong. Cached by chunk
   content hash so re-runs are free.

Results merge into the chunk's ``metadata`` dict before indexing.
Returns new Chunk instances rather than mutating inputs (Chunks frozen).
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
import os
import re
import sqlite3
from pathlib import Path
from typing import Any, Sequence

from src.ingest.chunking import Chunk

DEFAULT_MODEL = os.environ.get("GRAPH_METADATA_MODEL", "claude-haiku-4-5")
DEFAULT_CACHE_PATH = Path(os.environ.get("GRAPH_DATA_DIR", "./data")) / "metadata_cache.sqlite"

MANUFACTURERS = [
    "Lennox", "Carrier", "Trane", "Goodman", "Rheem", "York", "Daikin",
    "Mitsubishi", "Bryant", "Heil", "Amana", "Honeywell", "White-Rodgers",
    "Ecobee", "Emerson", "Copeland", "GE", "Marathon", "US Motors", "Fasco",
]

REFRIGERANTS = ["R-22", "R-410A", "R-32", "R-454B", "R-1234yf"]

REGULATIONS = [
    "AIM Act", "AIM-Act",
    "EPA SNAP", "EPA-SNAP", "SNAP Rule",
    "AHRI 210/240", "AHRI-210-240",
    "UL 60335-2-40", "UL-60335-2-40",
    "ASHRAE 34", "ASHRAE-34",
    "Section 232", "Section 301",
]

# Pre-compile case-insensitive word-boundary patterns.
_MFR_RE = re.compile(
    r"\b(" + "|".join(re.escape(m) for m in MANUFACTURERS) + r")\b",
    re.IGNORECASE,
)
_REF_RE = re.compile(
    r"\b(" + "|".join(re.escape(r) for r in REFRIGERANTS) + r")\b",
    re.IGNORECASE,
)
_REG_RE = re.compile(
    "(" + "|".join(re.escape(r) for r in REGULATIONS) + ")",
    re.IGNORECASE,
)
# SKU IDs look like the existing synthetic data: e.g. CAP-LEN-30MFD-0001.
_SKU_RE = re.compile(r"\b[A-Z]{3}-[A-Z]{2,4}-[A-Z0-9]{3,8}-\d{3,4}\b")


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _canonicalize_mfr(m: str) -> str:
    # Restore canonical casing.
    for canon in MANUFACTURERS:
        if m.lower() == canon.lower():
            return canon
    return m


def _canonicalize_refrigerant(r: str) -> str:
    for canon in REFRIGERANTS:
        if r.lower() == canon.lower():
            return canon
    return r.upper()


def _canonicalize_regulation(r: str) -> str:
    norm = r.replace(" ", "-").replace("/", "-")
    return norm


def _pattern_extract(text: str) -> dict[str, list[str]]:
    mfrs = sorted({_canonicalize_mfr(m) for m in _MFR_RE.findall(text)})
    refs = sorted({_canonicalize_refrigerant(r) for r in _REF_RE.findall(text)})
    regs = sorted({_canonicalize_regulation(r) for r in _REG_RE.findall(text)})
    skus = sorted(set(_SKU_RE.findall(text)))
    out: dict[str, list[str]] = {}
    if mfrs:
        out["mentioned_manufacturers"] = mfrs
    if refs:
        out["mentioned_refrigerants"] = refs
    if regs:
        out["mentioned_regulations"] = regs
    if skus:
        out["mentioned_skus"] = skus
    return out


# ---------------------------------------------------------------------------
# LLM path (optional)
# ---------------------------------------------------------------------------


_LLM_SYSTEM_PROMPT = """\
You extract entities mentioned in HVAC distributor documents.
Return only entities EXPLICITLY mentioned in the text — never infer.
"""

_LLM_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "manufacturers": {"type": "array", "items": {"type": "string"}},
        "refrigerants": {"type": "array", "items": {"type": "string"}},
        "regulations": {"type": "array", "items": {"type": "string"}},
        "skus": {"type": "array", "items": {"type": "string"}},
        "doc_type_override": {"type": ["string", "null"]},
    },
    "required": ["manufacturers", "refrigerants", "regulations", "skus", "doc_type_override"],
    "additionalProperties": False,
}


def _open_cache(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.execute(
        "CREATE TABLE IF NOT EXISTS chunk_meta ("
        "model TEXT NOT NULL, content_hash TEXT NOT NULL, payload TEXT NOT NULL, "
        "PRIMARY KEY (model, content_hash))"
    )
    return conn


def _llm_enrich_one(content: str, model: str, client: Any) -> dict[str, Any]:
    response = client.messages.create(
        model=model,
        max_tokens=512,
        system=_LLM_SYSTEM_PROMPT,
        tools=[{
            "name": "report_entities",
            "description": "Report entities mentioned in the chunk.",
            "input_schema": _LLM_SCHEMA,
        }],
        tool_choice={"type": "tool", "name": "report_entities"},
        messages=[{"role": "user", "content": content[:8000]}],
    )
    for block in response.content:
        if getattr(block, "type", None) == "tool_use":
            return block.input  # type: ignore[no-any-return]
    return {
        "manufacturers": [],
        "refrigerants": [],
        "regulations": [],
        "skus": [],
        "doc_type_override": None,
    }


def _llm_enrich_all(
    chunks: Sequence[Chunk],
    model: str,
    cache_path: Path,
) -> list[dict[str, Any]]:
    try:
        import anthropic
    except ImportError:
        print("[metadata] anthropic SDK not installed — skipping LLM enrichment")
        return [{} for _ in chunks]
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("[metadata] ANTHROPIC_API_KEY not set — skipping LLM enrichment")
        return [{} for _ in chunks]

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    conn = _open_cache(cache_path)
    try:
        out: list[dict[str, Any]] = []
        for c in chunks:
            h = _sha(c.content)
            row = conn.execute(
                "SELECT payload FROM chunk_meta WHERE model = ? AND content_hash = ?",
                (model, h),
            ).fetchone()
            if row:
                out.append(json.loads(row[0]))
                continue
            payload = _llm_enrich_one(c.content, model, client)
            conn.execute(
                "INSERT OR REPLACE INTO chunk_meta VALUES (?, ?, ?)",
                (model, h, json.dumps(payload)),
            )
            conn.commit()
            out.append(payload)
        return out
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def enrich_chunks(
    chunks: Sequence[Chunk],
    *,
    use_llm: bool = False,
    model: str | None = None,
    cache_path: Path | None = None,
) -> list[Chunk]:
    """Enrich each chunk with extracted-entity metadata."""
    if not chunks:
        return []
    model = model or DEFAULT_MODEL
    cache_path = cache_path or DEFAULT_CACHE_PATH

    pattern_results = [_pattern_extract(c.content) for c in chunks]
    llm_results: list[dict[str, Any]] = (
        _llm_enrich_all(chunks, model, cache_path) if use_llm else [{} for _ in chunks]
    )

    out: list[Chunk] = []
    for chunk, pmeta, lmeta in zip(chunks, pattern_results, llm_results):
        merged = dict(chunk.metadata)
        merged.update(pmeta)
        # LLM additions extend pattern results (union; LLM may catch long-tail).
        for src_key, dst_key in (
            ("manufacturers", "mentioned_manufacturers"),
            ("refrigerants", "mentioned_refrigerants"),
            ("regulations", "mentioned_regulations"),
            ("skus", "mentioned_skus"),
        ):
            extras = lmeta.get(src_key) or []
            if extras:
                merged[dst_key] = sorted(set(merged.get(dst_key, []) + extras))
        if lmeta.get("doc_type_override"):
            merged["doc_type_inferred"] = lmeta["doc_type_override"]
        out.append(dataclasses.replace(chunk, metadata=merged))
    return out
