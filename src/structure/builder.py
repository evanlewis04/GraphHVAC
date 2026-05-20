"""Wiki-page builder.

For each entity declared in ``concepts.yaml``:

  1. Enumerate instances via ``source_query`` (SQL) or ``source_static`` (list).
  2. For each instance, format ``retrieve_query`` and call
     ``src.retrieval.search.retrieve`` with the declared ``filters`` and ``k``.
  3. Synthesize a wiki page that cites every claim with the chunk_id of the
     supporting source. Two synthesis paths:
       - **LLM (Sonnet)** — when ``ANTHROPIC_API_KEY`` is set. Higher-quality
         prose, structured per the entity's ``required_fields``.
       - **Deterministic** — fallback when no key is set or ``--no-llm`` is
         passed. Composes the page from chunk snippets in a fixed layout.
         Lower quality but lets the whole pipeline run.
  4. Validate the output: every ``[chunk_id]`` reference points to a chunk
     in the retrieved set (no invented citations).
  5. Write the page to ``data/wiki/{wiki_dir}/{slug}.md`` with frontmatter:

         ---
         entity_type: refrigerant
         entity_id: R-410A
         slug: r-410a
         template_version: 1
         template_name: refrigerant
         last_built: 2026-05-18T10:32:00Z
         source_chunks: [chunk_id, ...]
         synthesizer: llm        # or "deterministic"
         ---

Build results are cached in ``data/structure_cache.sqlite`` keyed by
(entity_type, entity_id, sorted_chunk_ids_hash, template_version). Re-running
with unchanged inputs is free.

Default scope is the *new* entity types this phase introduces (refrigerants,
regulations, manufacturers, procedures). Existing entity types (skus,
suppliers, customers) have pre-existing template-rendered pages that this
builder skips unless ``--include-existing`` is passed.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import duckdb
import yaml

from src.retrieval.search import RetrievedChunk, retrieve

TEMPLATE_VERSION = 1

ROOT = Path(__file__).resolve().parents[2]
CONCEPTS_PATH = Path(__file__).with_name("concepts.yaml")
WIKI_DIR = Path(os.environ.get("GRAPH_WIKI_DIR", ROOT / "data" / "wiki"))
DUCKDB_PATH = Path(os.environ.get("GRAPH_DUCKDB_PATH", ROOT / "data" / "staging.duckdb"))
CACHE_PATH = Path(os.environ.get("GRAPH_DATA_DIR", ROOT / "data")) / "structure_cache.sqlite"

# Entity types we treat as "new" (built fresh by the structurer) vs "existing"
# (have pre-Phase-5 templated pages we skip unless asked).
NEW_ENTITY_TYPES = {"refrigerants", "regulations", "manufacturers", "procedures"}

_CITATION_RE = re.compile(r"\[([a-zA-Z0-9:_\-]+:\d{4}:[a-f0-9]{10})\]")


# ---------------------------------------------------------------------------
# Datatypes
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class BuildResult:
    entity_type: str
    entity_id: str
    wiki_path: Path
    source_chunk_ids: list[str] = field(default_factory=list)
    template_version: int = TEMPLATE_VERSION
    synthesizer: str = "deterministic"  # "llm" or "deterministic"
    cached: bool = False
    skipped_reason: str | None = None


# ---------------------------------------------------------------------------
# Cache
# ---------------------------------------------------------------------------


def _open_cache() -> sqlite3.Connection:
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(CACHE_PATH)
    conn.execute(
        "CREATE TABLE IF NOT EXISTS pages ("
        "entity_type TEXT NOT NULL, entity_id TEXT NOT NULL, key TEXT NOT NULL, "
        "body TEXT NOT NULL, synthesizer TEXT NOT NULL, "
        "PRIMARY KEY (entity_type, entity_id, key))"
    )
    return conn


def _cache_key(entity_id: str, chunk_ids: list[str], template_name: str) -> str:
    sig = entity_id + "|" + ",".join(sorted(chunk_ids)) + f"|{template_name}|v{TEMPLATE_VERSION}"
    return hashlib.sha256(sig.encode()).hexdigest()[:16]


def _cache_get(conn, entity_type: str, entity_id: str, key: str) -> tuple[str, str] | None:
    row = conn.execute(
        "SELECT body, synthesizer FROM pages WHERE entity_type = ? AND entity_id = ? AND key = ?",
        (entity_type, entity_id, key),
    ).fetchone()
    return (row[0], row[1]) if row else None


def _cache_put(conn, entity_type: str, entity_id: str, key: str, body: str, synth: str) -> None:
    conn.execute(
        "INSERT OR REPLACE INTO pages VALUES (?, ?, ?, ?, ?)",
        (entity_type, entity_id, key, body, synth),
    )
    conn.commit()


# ---------------------------------------------------------------------------
# Concepts.yaml loader + instance enumeration
# ---------------------------------------------------------------------------


def _load_concepts() -> dict[str, dict[str, Any]]:
    return yaml.safe_load(CONCEPTS_PATH.read_text(encoding="utf-8"))


def _enumerate_instances(concept: dict[str, Any]) -> list[dict[str, Any]]:
    """Return a list of instance dicts. Each has at least 'value' and 'slug'."""
    if concept["source_query"] == "static":
        return [
            {"value": v, "slug": _slugify(str(v)), "name": str(v)}
            for v in concept.get("source_static", [])
        ]
    # SQL path
    if not DUCKDB_PATH.exists():
        return []
    conn = duckdb.connect(str(DUCKDB_PATH), read_only=True)
    try:
        rows = conn.execute(concept["source_query"]).fetchall()
        cols = [d[0] for d in conn.description]
    finally:
        conn.close()
    out: list[dict[str, Any]] = []
    for row in rows:
        d = dict(zip(cols, row))
        # Prefer 'id' as the canonical instance key; fall back to first column.
        key = d.get("id") or d.get("name") or next(iter(d.values()))
        d["value"] = key
        d["slug"] = _slugify(str(key))
        d["name"] = str(d.get("name") or key)
        out.append(d)
    return out


def _slugify(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def _format_with_instance(template: str, instance: dict[str, Any]) -> str:
    """Format a string with instance fields, leaving unknown placeholders intact."""
    class _Default(dict):
        def __missing__(self, key):
            return f"{{{key}}}"
    return template.format_map(_Default(instance))


def _interpolate_filters(filters: dict[str, Any] | None, instance: dict[str, Any]) -> dict[str, Any]:
    if not filters:
        return {}
    return {k: _format_with_instance(str(v), instance) for k, v in filters.items()}


# ---------------------------------------------------------------------------
# Synthesis
# ---------------------------------------------------------------------------


_LLM_SYSTEM_PROMPT = """\
You write wiki entries for an HVAC parts distributor.

You will be given an entity (e.g. a refrigerant, regulation, or manufacturer),
a list of source chunks already retrieved from the corpus, and the required
sections to cover.

Rules — non-negotiable:

1. Every factual claim in your output MUST be supported by one of the
   provided chunks and cited inline as [chunk_id] using the EXACT chunk_id
   string from the source list. You may cite multiple chunks: [c1][c2].
2. Never invent chunk_ids. If you don't have a chunk to support a claim,
   omit the claim.
3. Cover each required section as an H2 heading. If a section has no
   supporting chunks, write "_No source coverage._" under it — do not
   fabricate content.
4. Output ONLY the markdown body — no frontmatter, no opening commentary.
   The first line should be a single H1 with the entity title.
5. Be concise. The wiki reader is an HVAC operations lead, not a student.
"""


def _build_llm_user_prompt(
    concept: dict[str, Any],
    instance: dict[str, Any],
    chunks: list[RetrievedChunk],
) -> str:
    chunk_blocks = []
    for c in chunks:
        head = " > ".join(c.heading_path) if c.heading_path else "—"
        chunk_blocks.append(
            f"---\nCHUNK ID: {c.chunk_id}\nSOURCE: {c.source_id}\nHEADING: {head}\n\n{c.snippet}\n"
            f"\n[full content follows]\n{c.metadata.get('content_preview', '')}"
        )
    chunks_text = "\n".join(chunk_blocks) if chunk_blocks else "(no chunks retrieved)"
    required = ", ".join(concept.get("required_fields") or [])
    return (
        f"ENTITY TYPE: {concept.get('wiki_dir', '?')}\n"
        f"ENTITY ID: {instance['value']}\n"
        f"ENTITY NAME: {instance.get('name', instance['value'])}\n"
        f"REQUIRED SECTIONS: {required}\n"
        f"\nSOURCE CHUNKS:\n{chunks_text}\n"
        f"\nWrite the wiki page now. Cite using EXACT chunk_id strings in [brackets]."
    )


def _synthesize_llm(
    concept: dict[str, Any],
    instance: dict[str, Any],
    chunks: list[RetrievedChunk],
) -> str | None:
    """Call Sonnet to synthesize. Returns None if API unavailable."""
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return None
    try:
        import anthropic
    except ImportError:
        return None
    # Inline a fuller chunk text into the prompt (snippet alone is truncated).
    enriched: list[RetrievedChunk] = []
    for c in chunks:
        full = _full_chunk_text(c.chunk_id) or c.snippet
        enriched.append(RetrievedChunk(
            citation_id="",
            chunk_id=c.chunk_id,
            source_id=c.source_id,
            snippet=full[:1800],
            score=c.score,
            bm25_score=c.bm25_score,
            vector_score=c.vector_score,
            rerank_score=c.rerank_score,
            heading_path=list(c.heading_path),
            page_range=c.page_range,
            metadata=c.metadata,
        ))

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    model = os.environ.get("GRAPH_COMPILER_MODEL", "claude-sonnet-4-6")
    try:
        resp = client.messages.create(
            model=model,
            max_tokens=2048,
            system=_LLM_SYSTEM_PROMPT,
            messages=[{
                "role": "user",
                "content": _build_llm_user_prompt(concept, instance, enriched),
            }],
        )
    except Exception as exc:
        print(f"[structure] LLM call failed for {instance['value']}: {exc}")
        return None
    return "\n".join(b.text for b in resp.content if b.type == "text").strip()


def _full_chunk_text(chunk_id: str) -> str | None:
    """Look up full chunk content from LanceDB."""
    from src.retrieval.search import _load_chunks
    from src.retrieval.index import DEFAULT_LANCEDB_PATH
    chunks = _load_chunks(str(DEFAULT_LANCEDB_PATH))
    row = chunks.get(chunk_id)
    return row["content"] if row else None


def _synthesize_deterministic(
    concept: dict[str, Any],
    instance: dict[str, Any],
    chunks: list[RetrievedChunk],
) -> str:
    """Compose a no-LLM page that lists source snippets under required sections.

    Honest about its limitations: the page header marks itself as
    deterministically composed so reviewers know what they're looking at.
    """
    name = instance.get("name") or instance["value"]
    lines: list[str] = [f"# {name}\n"]
    lines.append(
        "_This page was assembled without LLM synthesis (no `ANTHROPIC_API_KEY` "
        "or `--no-llm` was used). Content below is a structured list of "
        "supporting source chunks; set the API key and rebuild for narrative "
        "synthesis._\n"
    )
    if not chunks:
        lines.append("_No source chunks were retrieved for this entity._\n")
        return "\n".join(lines)

    required = concept.get("required_fields") or ["Overview"]
    for field_name in required:
        lines.append(f"## {field_name.replace('_', ' ').title()}\n")
        # Pick chunks whose heading_path mentions the field name (loose match);
        # fall back to first 2 chunks for the first section.
        matched = [
            c for c in chunks
            if field_name.lower() in " ".join(c.heading_path).lower()
        ]
        if not matched and field_name == required[0]:
            matched = chunks[:2]
        if not matched:
            lines.append("_No source coverage._\n")
            continue
        for c in matched:
            full = _full_chunk_text(c.chunk_id) or c.snippet
            excerpt = full[:600].rstrip() + ("…" if len(full) > 600 else "")
            lines.append(f"> {excerpt} [{c.chunk_id}]\n")

    # Any chunks that didn't match a required section get a catch-all.
    all_cited = {c.chunk_id for c in chunks if any(
        f.lower() in " ".join(c.heading_path).lower()
        for f in (concept.get("required_fields") or [])
    )}
    leftover = [c for c in chunks if c.chunk_id not in all_cited]
    if leftover:
        lines.append("## Additional Source Material\n")
        for c in leftover:
            full = _full_chunk_text(c.chunk_id) or c.snippet
            excerpt = full[:400].rstrip() + ("…" if len(full) > 400 else "")
            lines.append(f"> {excerpt} [{c.chunk_id}]\n")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def _validate(body: str, allowed_chunk_ids: set[str]) -> list[str]:
    """Return a list of validation warnings (empty if clean)."""
    warnings: list[str] = []
    found = _CITATION_RE.findall(body)
    invented = [c for c in found if c not in allowed_chunk_ids]
    if invented:
        warnings.append(f"invented_chunk_ids: {sorted(set(invented))[:5]}")
    cited = set(found) & allowed_chunk_ids
    if not cited:
        warnings.append("no_citations_in_body")
    return warnings


# ---------------------------------------------------------------------------
# Page writing
# ---------------------------------------------------------------------------


def _write_page(
    entity_type: str,
    instance: dict[str, Any],
    concept: dict[str, Any],
    body: str,
    chunk_ids: list[str],
    synthesizer: str,
    warnings: list[str],
) -> Path:
    wiki_dir = WIKI_DIR / concept["wiki_dir"]
    wiki_dir.mkdir(parents=True, exist_ok=True)
    slug = instance["slug"]
    path = wiki_dir / f"{slug}.md"
    frontmatter = {
        "entity_type": entity_type,
        "entity_id": str(instance["value"]),
        "slug": slug,
        "template_version": TEMPLATE_VERSION,
        "template_name": concept.get("template", "default"),
        "last_built": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source_chunks": chunk_ids,
        "synthesizer": synthesizer,
    }
    if warnings:
        frontmatter["validation_warnings"] = warnings
    fm = yaml.safe_dump(frontmatter, sort_keys=False).strip()
    path.write_text(f"---\n{fm}\n---\n\n{body}\n", encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def build_entity(
    entity_type: str,
    entity_id: str | None = None,
    *,
    use_llm: bool = True,
    force: bool = False,
) -> BuildResult:
    """Build a single wiki page.

    If ``entity_id`` is None, enumerate the entity type and build the first
    matching instance (useful for spot tests).
    """
    concepts = _load_concepts()
    if entity_type not in concepts:
        raise KeyError(f"Unknown entity type {entity_type!r} in concepts.yaml")
    concept = concepts[entity_type]
    instances = _enumerate_instances(concept)
    if entity_id is None:
        if not instances:
            raise RuntimeError(f"No instances of {entity_type!r} found")
        target = instances[0]
    else:
        matches = [i for i in instances if str(i["value"]) == str(entity_id)]
        if not matches:
            raise KeyError(f"No instance {entity_id!r} for {entity_type!r}")
        target = matches[0]
    return _build_one(entity_type, target, concept, use_llm=use_llm, force=force)


def _build_one(
    entity_type: str,
    instance: dict[str, Any],
    concept: dict[str, Any],
    *,
    use_llm: bool,
    force: bool,
) -> BuildResult:
    query = _format_with_instance(concept["retrieve_query"], instance)
    filters = _interpolate_filters(concept.get("filters"), instance)
    chunks = retrieve(
        query,
        k=concept.get("retrieve_k", 8),
        filters=filters,
        rerank=False,  # rerank is opt-in; saves Voyage credits in batch builds
    )
    chunk_ids = [c.chunk_id for c in chunks]

    conn = _open_cache()
    cache_key = _cache_key(str(instance["value"]), chunk_ids, concept.get("template", "default"))
    cached = None if force else _cache_get(conn, entity_type, str(instance["value"]), cache_key)

    if cached is not None:
        body, synthesizer = cached
        warnings: list[str] = []
        was_cached = True
    else:
        synthesizer = "llm" if use_llm and os.environ.get("ANTHROPIC_API_KEY") else "deterministic"
        body = None
        if synthesizer == "llm":
            body = _synthesize_llm(concept, instance, chunks)
            if body is None:
                # LLM call failed — fall back to deterministic so we still write something.
                synthesizer = "deterministic"
        if body is None:
            body = _synthesize_deterministic(concept, instance, chunks)
        warnings = _validate(body, set(chunk_ids))
        _cache_put(conn, entity_type, str(instance["value"]), cache_key, body, synthesizer)
        was_cached = False

    conn.close()
    path = _write_page(entity_type, instance, concept, body, chunk_ids, synthesizer, warnings)
    return BuildResult(
        entity_type=entity_type,
        entity_id=str(instance["value"]),
        wiki_path=path,
        source_chunk_ids=chunk_ids,
        template_version=TEMPLATE_VERSION,
        synthesizer=synthesizer,
        cached=was_cached,
    )


def build_all(
    *,
    only: list[str] | None = None,
    include_existing: bool = False,
    limit_per_type: int | None = None,
    use_llm: bool = True,
    force: bool = False,
    on_progress=None,
) -> list[BuildResult]:
    """Build every page declared in ``concepts.yaml``.

    By default builds only the NEW entity types introduced in Phase 5
    (refrigerants, regulations, manufacturers, procedures). The existing
    entity types (skus, suppliers, customers) have pre-Phase-5 templated
    pages and are skipped unless ``include_existing=True`` or named in
    ``only=[...]``.

    ``limit_per_type`` caps per-type instance count (useful for spot-checks).
    """
    concepts = _load_concepts()
    results: list[BuildResult] = []
    types_to_build = list(only) if only else [
        t for t in concepts if include_existing or t in NEW_ENTITY_TYPES
    ]
    for entity_type in types_to_build:
        if entity_type not in concepts:
            results.append(BuildResult(
                entity_type=entity_type, entity_id="",
                wiki_path=Path(),
                skipped_reason="unknown entity type",
            ))
            continue
        concept = concepts[entity_type]
        instances = _enumerate_instances(concept)
        if limit_per_type is not None:
            instances = instances[:limit_per_type]
        for instance in instances:
            try:
                result = _build_one(entity_type, instance, concept, use_llm=use_llm, force=force)
            except Exception as exc:
                result = BuildResult(
                    entity_type=entity_type,
                    entity_id=str(instance.get("value", "?")),
                    wiki_path=Path(),
                    skipped_reason=f"{type(exc).__name__}: {exc}",
                )
            results.append(result)
            if on_progress:
                on_progress(result)
    return results


# ---------------------------------------------------------------------------
# Frontmatter helpers (shared with freshness.py / health.py)
# ---------------------------------------------------------------------------


_FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


def parse_page_frontmatter(path: Path) -> dict[str, Any] | None:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None
    m = _FRONTMATTER_RE.match(text)
    if not m:
        return None
    try:
        return yaml.safe_load(m.group(1))
    except yaml.YAMLError:
        return None


def iter_structurer_pages(wiki_dir: Path | None = None):
    """Yield (path, frontmatter) for every wiki page built by the structurer."""
    wiki_dir = wiki_dir or WIKI_DIR
    if not wiki_dir.exists():
        return
    for path in wiki_dir.rglob("*.md"):
        fm = parse_page_frontmatter(path)
        if fm and "source_chunks" in fm and "template_version" in fm:
            yield path, fm


def stringify_summary(results: list[BuildResult]) -> str:
    counts: dict[str, dict[str, int]] = {}
    for r in results:
        bucket = counts.setdefault(r.entity_type, {"built": 0, "cached": 0, "skipped": 0})
        if r.skipped_reason:
            bucket["skipped"] += 1
        elif r.cached:
            bucket["cached"] += 1
        else:
            bucket["built"] += 1
    return json.dumps(counts, indent=2)
