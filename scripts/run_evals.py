"""Run the golden-set evaluation.

Default mode is retrieval-only: queries the live LanceDB + BM25 index for
each golden question and scores recall@5 / recall@10 / MRR. No API key
required.

Agent mode (``--mode agent``) runs each question through the full agent
loop. Requires ``ANTHROPIC_API_KEY``. Adds citation precision / recall +
latency + token usage to the scoring.

Outputs:
  - data/evals/<run_id>.jsonl          — one row per question
  - data/evals/<run_id>.summary.json   — aggregate metrics

Both files are picked up by Admin → Evals in the UI.

Examples:
    python scripts/run_evals.py
    python scripts/run_evals.py --mode agent
    python scripts/run_evals.py --golden tests/eval/golden.jsonl --k 10
    python scripts/run_evals.py --run-id 2026-05-19-bm25-only
"""

from __future__ import annotations

import argparse
from pathlib import Path

from src.eval.runner import run_eval

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GOLDEN = ROOT / "tests" / "eval" / "golden.jsonl"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--golden", type=Path, default=DEFAULT_GOLDEN)
    parser.add_argument("--mode", choices=["retrieval", "agent"], default="retrieval")
    parser.add_argument("--k", type=int, default=10,
                        help="Top-k chunks per query for retrieval scoring.")
    parser.add_argument("--run-id", default=None,
                        help="Override the auto-generated run id (timestamp + mode).")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    if not args.golden.exists():
        raise SystemExit(f"golden set not found: {args.golden}")

    def _on_progress(score):
        if args.quiet:
            return
        tag = "HIT " if score.recall_at_5 > 0 else "MISS"
        rr = score.reciprocal_rank
        retrieved = ", ".join(score.retrieved_source_ids[:3]) + (
            "…" if len(score.retrieved_source_ids) > 3 else ""
        )
        print(f"[{tag}] {score.qid}  RR={rr:.2f}  expected={score.expected_source_ids}")
        print(f"        top retrieved: {retrieved}")

    jsonl_path, summary = run_eval(
        args.golden, mode=args.mode, k=args.k,
        run_id=args.run_id, on_progress=_on_progress,
    )

    print()
    print("=== Eval summary ===")
    print(f"questions:        {summary.n_questions}")
    print(f"recall@5:         {summary.recall_at_5:.3f}")
    print(f"recall@10:        {summary.recall_at_10:.3f}")
    print(f"MRR:              {summary.mrr:.3f}")
    if summary.citation_precision is not None:
        print(f"citation prec:    {summary.citation_precision:.3f}")
        print(f"citation recall:  {summary.citation_recall:.3f}")
    if summary.latency_p50_ms is not None:
        print(f"latency p50:      {summary.latency_p50_ms} ms")
        print(f"latency p95:      {summary.latency_p95_ms} ms")
    if summary.avg_cost_usd is not None:
        print(f"avg cost/query:   ${summary.avg_cost_usd:.4f}")
    print()
    print(f"per-question -> {jsonl_path}")
    print(f"summary      -> {jsonl_path.with_name(jsonl_path.stem + '.summary.json')}")


if __name__ == "__main__":
    main()
