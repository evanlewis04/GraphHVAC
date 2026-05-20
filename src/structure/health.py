"""Knowledge-health checks.

Walks the structured wiki + retrieval corpus and flags:

  - **Orphan chunks**: chunks indexed in retrieval but not cited by any
    structurer-built wiki page — candidate material for new pages or
    page expansions.
  - **Thin coverage**: pages with fewer than ``min_chunks`` source
    citations (default 2).
  - **Dangling wikilinks**: ``[[...]]`` references that don't resolve
    to any markdown file in ``data/wiki/``.
  - **Validation warnings**: pages whose frontmatter has a non-empty
    ``validation_warnings`` field (carried forward from the builder).
  - **Contradictions** (LLM-only, opt-in): sample pages of the same
    entity type and ask the model if they conflict. Skipped without
    an ``ANTHROPIC_API_KEY`` or when ``use_llm=False``.

Output: a structured ``HealthReport`` returned to callers AND written
to ``data/wiki/concepts/health-check.md`` for browsing.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import lancedb

from src.retrieval.index import DEFAULT_LANCEDB_PATH, TABLE_NAME
from src.structure.builder import (
    WIKI_DIR,
    iter_structurer_pages,
    parse_page_frontmatter,
)

_WIKILINK_RE = re.compile(r"\[\[([^\]|]+?)(?:\|[^\]]+)?\]\]")


@dataclass(frozen=True)
class HealthReport:
    generated_at: str
    chunks_total: int
    chunks_cited: int
    pages_total: int
    orphan_chunks: list[str] = field(default_factory=list)
    thin_pages: list[dict[str, Any]] = field(default_factory=list)
    dangling_links: list[dict[str, Any]] = field(default_factory=list)
    validation_warnings: list[dict[str, Any]] = field(default_factory=list)
    contradictions: list[dict[str, Any]] = field(default_factory=list)
    coverage_by_bucket: dict[str, dict[str, int]] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _load_all_chunks() -> list[dict[str, Any]]:
    if not DEFAULT_LANCEDB_PATH.exists():
        return []
    db = lancedb.connect(str(DEFAULT_LANCEDB_PATH))
    if TABLE_NAME not in db.table_names():
        return []
    return db.open_table(TABLE_NAME).to_arrow().to_pylist()


def _all_wiki_paths(wiki_dir: Path) -> set[str]:
    """Set of resolvable wikilink targets, with and without `.md`."""
    out: set[str] = set()
    if not wiki_dir.exists():
        return out
    for p in wiki_dir.rglob("*.md"):
        rel = p.relative_to(wiki_dir).as_posix()
        out.add(rel)
        out.add(rel.removesuffix(".md"))
    return out


def _resolve_wikilink(target: str, wiki_paths: set[str]) -> bool:
    candidates = [
        target,
        f"{target}.md",
        target.removesuffix(".md"),
    ]
    return any(c in wiki_paths for c in candidates)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def run_health_check(
    *,
    min_chunks: int = 2,
    use_llm: bool = False,
    sample_for_contradictions: int = 6,
    write_report: bool = True,
    wiki_dir: Path | None = None,
) -> HealthReport:
    wiki_dir = wiki_dir or WIKI_DIR
    chunks = _load_all_chunks()
    wiki_paths = _all_wiki_paths(wiki_dir)

    cited: set[str] = set()
    pages_total = 0
    thin: list[dict[str, Any]] = []
    dangling: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    coverage_by_bucket: dict[str, dict[str, int]] = {}

    pages_for_contra: list[tuple[Path, dict[str, Any]]] = []

    for path, fm in iter_structurer_pages(wiki_dir):
        pages_total += 1
        page_chunks = list(fm.get("source_chunks") or [])
        cited.update(page_chunks)
        if len(page_chunks) < min_chunks:
            thin.append({
                "wiki_path": str(path.relative_to(wiki_dir)),
                "entity_type": fm.get("entity_type"),
                "entity_id": fm.get("entity_id"),
                "chunk_count": len(page_chunks),
            })
        if fm.get("validation_warnings"):
            warnings.append({
                "wiki_path": str(path.relative_to(wiki_dir)),
                "warnings": fm["validation_warnings"],
            })
        # Dangling wikilinks in the body
        try:
            body = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            body = ""
        for m in _WIKILINK_RE.finditer(body):
            target = m.group(1).strip()
            if not _resolve_wikilink(target, wiki_paths):
                dangling.append({
                    "wiki_path": str(path.relative_to(wiki_dir)),
                    "missing_target": target,
                })

        pages_for_contra.append((path, fm))

    # Coverage rollup by bucket — based on UNIQUE cited chunks per bucket
    # so multi-cited chunks don't inflate the count past 100%.
    bucket_totals: dict[str, int] = {}
    bucket_cited: dict[str, set[str]] = {}
    for chunk in chunks:
        bucket = chunk.get("bucket") or "?"
        bucket_totals[bucket] = bucket_totals.get(bucket, 0) + 1
        if chunk["chunk_id"] in cited:
            bucket_cited.setdefault(bucket, set()).add(chunk["chunk_id"])
    for bucket, total in bucket_totals.items():
        coverage_by_bucket[bucket] = {
            "cited": len(bucket_cited.get(bucket, set())),
            "total": total,
        }

    orphans = sorted(c["chunk_id"] for c in chunks if c["chunk_id"] not in cited)

    contradictions: list[dict[str, Any]] = []
    if use_llm and os.environ.get("ANTHROPIC_API_KEY"):
        contradictions = _llm_find_contradictions(pages_for_contra, sample_for_contradictions)

    report = HealthReport(
        generated_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        chunks_total=len(chunks),
        chunks_cited=len(cited),
        pages_total=pages_total,
        orphan_chunks=orphans,
        thin_pages=thin,
        dangling_links=dangling,
        validation_warnings=warnings,
        contradictions=contradictions,
        coverage_by_bucket=coverage_by_bucket,
    )

    if write_report:
        _write_report_page(report, wiki_dir)
    return report


# ---------------------------------------------------------------------------
# LLM contradiction check (opt-in)
# ---------------------------------------------------------------------------


def _llm_find_contradictions(
    pages: list[tuple[Path, dict[str, Any]]],
    sample_n: int,
) -> list[dict[str, Any]]:
    try:
        import anthropic
    except ImportError:
        return []
    if not pages:
        return []
    # Group by entity_type; sample within each.
    by_type: dict[str, list[tuple[Path, dict[str, Any]]]] = {}
    for path, fm in pages:
        by_type.setdefault(fm.get("entity_type", "?"), []).append((path, fm))

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    model = os.environ.get("GRAPH_COMPILER_MODEL", "claude-sonnet-4-6")
    findings: list[dict[str, Any]] = []
    for entity_type, group in by_type.items():
        sample = group[:sample_n]
        bodies = []
        for path, _fm in sample:
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            bodies.append(f"### {path.name}\n{text[:2500]}")
        if len(bodies) < 2:
            continue
        prompt = (
            f"You are auditing an HVAC distributor wiki for contradictions among "
            f"{entity_type} pages.\n\nReview the following pages and list any "
            f"factual contradictions (same fact stated two different ways across "
            f"pages). If none, say 'NONE'. Be concise; one bullet per "
            f"contradiction.\n\n" + "\n\n".join(bodies)
        )
        try:
            resp = client.messages.create(
                model=model, max_tokens=1024,
                messages=[{"role": "user", "content": prompt}],
            )
        except Exception as exc:
            findings.append({"entity_type": entity_type, "error": str(exc)})
            continue
        text = "\n".join(b.text for b in resp.content if b.type == "text").strip()
        if text and text.upper() != "NONE":
            findings.append({"entity_type": entity_type, "report": text})
    return findings


# ---------------------------------------------------------------------------
# Report page
# ---------------------------------------------------------------------------


def _write_report_page(report: HealthReport, wiki_dir: Path) -> Path:
    concepts_dir = wiki_dir / "concepts"
    concepts_dir.mkdir(parents=True, exist_ok=True)
    path = concepts_dir / "health-check.md"
    lines: list[str] = [
        "---",
        "type: concept",
        "topic: Knowledge health check",
        f"generated_at: {report.generated_at}",
        "---",
        "",
        "# Knowledge Health Check",
        "",
        f"_Generated {report.generated_at}_",
        "",
        "## Summary",
        f"- Wiki pages (structurer-built): **{report.pages_total}**",
        f"- Chunks in retrieval: **{report.chunks_total}**",
        f"- Chunks cited by at least one wiki page: **{report.chunks_cited}**",
        f"- Orphan chunks (not cited anywhere): **{len(report.orphan_chunks)}**",
        f"- Thin pages (< 2 source chunks): **{len(report.thin_pages)}**",
        f"- Dangling wikilinks: **{len(report.dangling_links)}**",
        f"- Pages with validation warnings: **{len(report.validation_warnings)}**",
        f"- Contradiction findings: **{len(report.contradictions)}**",
        "",
        "## Coverage by bucket",
        "",
        "| Bucket | Cited chunks | Total chunks | Coverage |",
        "| --- | --- | --- | --- |",
    ]
    for bucket, d in sorted(report.coverage_by_bucket.items()):
        total = d.get("total", 0)
        cited = d.get("cited", 0)
        pct = f"{(cited / total * 100):.0f}%" if total else "—"
        lines.append(f"| {bucket} | {cited} | {total} | {pct} |")

    if report.thin_pages:
        lines += ["", "## Thin pages (< 2 chunks)", ""]
        for tp in report.thin_pages[:30]:
            lines.append(
                f"- **{tp['entity_type']}/{tp['entity_id']}** "
                f"({tp['chunk_count']} chunks) — `{tp['wiki_path']}`"
            )
        if len(report.thin_pages) > 30:
            lines.append(f"- … and {len(report.thin_pages) - 30} more")

    if report.dangling_links:
        lines += ["", "## Dangling wikilinks", ""]
        for d in report.dangling_links[:30]:
            lines.append(f"- `{d['wiki_path']}` → `[[{d['missing_target']}]]`")
        if len(report.dangling_links) > 30:
            lines.append(f"- … and {len(report.dangling_links) - 30} more")

    if report.validation_warnings:
        lines += ["", "## Validation warnings", ""]
        for w in report.validation_warnings[:30]:
            lines.append(f"- `{w['wiki_path']}`: {w['warnings']}")

    if report.contradictions:
        lines += ["", "## LLM contradiction findings", ""]
        for c in report.contradictions:
            lines.append(f"### {c.get('entity_type', '?')}")
            lines.append(c.get("report", c.get("error", "")))
            lines.append("")

    if report.orphan_chunks:
        lines += ["", "## Orphan chunks (not cited)", ""]
        lines.append(f"_{len(report.orphan_chunks)} chunks; sampling first 30:_")
        for cid in report.orphan_chunks[:30]:
            lines.append(f"- `{cid}`")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


# Re-export for callers that want frontmatter parsing
__all__ = ["HealthReport", "run_health_check", "parse_page_frontmatter"]
