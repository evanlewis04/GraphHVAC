"""Evaluation harness.

Runs a hand-authored golden set of questions through the full agent loop
and scores both retrieval quality and answer quality.

  - ``runner.py`` — orchestrates the eval, hits the agent, collects outputs.
  - ``metrics.py`` — recall@k, MRR, citation precision, claim coverage,
    cost, latency.

Golden set lives at ``tests/eval/golden.jsonl`` (Phase 8).
"""
