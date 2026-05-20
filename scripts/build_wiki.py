"""Build / rebuild the structured wiki from the ingested source corpus.

By default builds the entity types introduced in Phase 5 (refrigerants,
regulations, manufacturers, procedures) — about 32 pages total. Pre-existing
templated SKU/supplier/customer pages are left alone unless you pass
``--include-existing``.

Examples:
    python scripts/build_wiki.py
    python scripts/build_wiki.py --only refrigerants
    python scripts/build_wiki.py --rebuild-stale
    python scripts/build_wiki.py --health
    python scripts/build_wiki.py --no-llm           # force deterministic
    python scripts/build_wiki.py --limit-per-type 3 # spot-check
"""

from __future__ import annotations

import argparse
import time

from src.structure import builder, freshness, health


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", nargs="+", default=None,
                        help="Restrict to specific entity types.")
    parser.add_argument("--include-existing", action="store_true",
                        help="Also rebuild pre-Phase-5 entity types (skus, suppliers, customers).")
    parser.add_argument("--limit-per-type", type=int, default=None,
                        help="Cap instance count per entity type.")
    parser.add_argument("--no-llm", action="store_true",
                        help="Use deterministic synthesis even if ANTHROPIC_API_KEY is set.")
    parser.add_argument("--force", action="store_true",
                        help="Ignore the structure_cache and rebuild every page.")
    parser.add_argument("--rebuild-stale", action="store_true",
                        help="Skip the regular build; rebuild only stale pages.")
    parser.add_argument("--health", action="store_true",
                        help="Run the health check after building (and write the report page).")
    parser.add_argument("--health-llm", action="store_true",
                        help="Include LLM-driven contradiction detection in --health.")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    use_llm = not args.no_llm

    t0 = time.time()
    if args.rebuild_stale:
        results = freshness.rebuild_stale(
            use_llm=use_llm, force=args.force,
            on_progress=None if args.quiet else _printer(),
        )
        print(f"\nrebuilt {len(results)} stale pages in {time.time() - t0:.1f}s")
    else:
        results = builder.build_all(
            only=args.only,
            include_existing=args.include_existing,
            limit_per_type=args.limit_per_type,
            use_llm=use_llm,
            force=args.force,
            on_progress=None if args.quiet else _printer(),
        )
        print(f"\nbuilt {len(results)} pages in {time.time() - t0:.1f}s")
    print(builder.stringify_summary(results))

    if args.health:
        report = health.run_health_check(use_llm=args.health_llm)
        print()
        print(f"health check: {report.pages_total} pages, "
              f"{report.chunks_cited}/{report.chunks_total} chunks cited, "
              f"{len(report.orphan_chunks)} orphans, "
              f"{len(report.thin_pages)} thin, "
              f"{len(report.dangling_links)} dangling links")
        print("report -> data/wiki/concepts/health-check.md")


def _printer():
    def _print(r):
        tag = ("[cache]" if r.cached else "[built]") if not r.skipped_reason else "[SKIP]"
        rhs = r.skipped_reason or (f"-> {r.wiki_path.name}  ({r.synthesizer})")
        print(f"{tag} {r.entity_type}/{r.entity_id}  {rhs}")
    return _print


if __name__ == "__main__":
    main()
