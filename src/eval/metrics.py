"""Eval scoring.

Two families of metrics, computed at the **source level** rather than the
chunk level. Chunk_ids are content-hashed and change whenever a source's
content changes — using them as ground truth would make golden records
break every time we tweak a document. Source_ids are stable.

**Retrieval** (computed from the source_ids of the chunks ``retrieve()``
returned, vs the ``expected_source_ids`` in the golden record):

  - ``recall@5``, ``recall@10`` — fraction of questions where at least
    one expected source appeared in the top-k retrieved chunks
  - ``MRR`` (mean reciprocal rank) — averaged 1 / rank_of_first_hit;
    questions with no hit contribute 0

**Answer** (only available when ``--mode agent`` is used; needs a live
API key):

  - ``citation_precision``: fraction of cited source_ids that were in
    the expected set
  - ``citation_recall``: fraction of expected source_ids that were cited
  - ``claim_coverage`` (LLM-judge, opt-in): fraction of atomic claims
    in the answer that the judge marks as supported by cited chunks

Rolled up: latency p50/p95, cost-per-question from token counts.
"""

from __future__ import annotations

import json
import statistics
from dataclasses import asdict, dataclass, field
from pathlib import Path


def _base_source_id(sid: str) -> str:
    """Strip per-message / per-ticket suffix from a source_id."""
    return sid.split("#", 1)[0]


@dataclass(frozen=True)
class PerQuestionScore:
    qid: str
    question: str
    expected_source_ids: list[str]
    retrieved_source_ids: list[str]
    cited_source_ids: list[str] = field(default_factory=list)
    recall_at_5: float = 0.0
    recall_at_10: float = 0.0
    reciprocal_rank: float = 0.0
    citation_precision: float | None = None
    citation_recall: float | None = None
    latency_ms: int | None = None
    model: str | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None
    cache_read_input_tokens: int | None = None
    cache_creation_input_tokens: int | None = None
    error: str | None = None


@dataclass(frozen=True)
class MetricsSummary:
    n_questions: int
    recall_at_5: float
    recall_at_10: float
    mrr: float
    citation_precision: float | None
    citation_recall: float | None
    claim_coverage: float | None
    unsupported_claims_total: int | None
    latency_p50_ms: int | None
    latency_p95_ms: int | None
    avg_input_tokens: float | None
    avg_output_tokens: float | None
    avg_cost_usd: float | None
    by_qid: list[dict] = field(default_factory=list)


# --- Token pricing (USD per 1M tokens, list price as of 2026-07). Cheap
# approximation — used only to put a $/query number in the eval summary, not
# for billing. Keyed by GRAPH_AGENT_MODEL value so cost is correct regardless
# of which model actually ran.
MODEL_PRICES: dict[str, tuple[float, float]] = {
    # model_id -> (input $/1M, output $/1M)
    "claude-opus-4-8": (5.00, 25.00),
    "claude-opus-4-7": (5.00, 25.00),
    "claude-opus-4-6": (5.00, 25.00),
    "claude-sonnet-5": (2.00, 10.00),  # intro pricing through 2026-08-31; standard is 3.00/15.00
    "claude-sonnet-4-6": (3.00, 15.00),
    "claude-haiku-4-5": (1.00, 5.00),
}

# Prompt-cache pricing is a multiplier on the base input price: writes cost
# a premium (5-minute TTL, the only TTL this agent uses — see loop.py's
# `cache_control`), reads are heavily discounted.
CACHE_WRITE_MULTIPLIER = 1.25
CACHE_READ_MULTIPLIER = 0.1


def _cost(
    model: str | None,
    input_tokens: int | None,
    output_tokens: int | None,
    cache_read_input_tokens: int | None = None,
    cache_creation_input_tokens: int | None = None,
) -> float | None:
    if model is None or input_tokens is None or output_tokens is None:
        return None
    prices = MODEL_PRICES.get(model)
    if prices is None:
        return None
    price_in, price_out = prices
    cost = input_tokens * price_in / 1_000_000 + output_tokens * price_out / 1_000_000
    cost += (cache_read_input_tokens or 0) * price_in * CACHE_READ_MULTIPLIER / 1_000_000
    cost += (cache_creation_input_tokens or 0) * price_in * CACHE_WRITE_MULTIPLIER / 1_000_000
    return cost


def score_question(
    qid: str,
    question: str,
    expected_source_ids: list[str],
    retrieved_source_ids: list[str],
    cited_source_ids: list[str] | None = None,
    latency_ms: int | None = None,
    model: str | None = None,
    input_tokens: int | None = None,
    output_tokens: int | None = None,
    cache_read_input_tokens: int | None = None,
    cache_creation_input_tokens: int | None = None,
    error: str | None = None,
) -> PerQuestionScore:
    """Score one question."""
    expected = {_base_source_id(s) for s in expected_source_ids}
    retrieved_bases = [_base_source_id(s) for s in retrieved_source_ids]

    # recall@k — 1 if any of the first k retrieved sources is in expected
    def _recall_at(k: int) -> float:
        if not expected:
            return 0.0
        return 1.0 if any(s in expected for s in retrieved_bases[:k]) else 0.0

    # reciprocal rank — 1/(rank of first relevant) or 0
    rr = 0.0
    for i, s in enumerate(retrieved_bases, start=1):
        if s in expected:
            rr = 1.0 / i
            break

    cite_p: float | None = None
    cite_r: float | None = None
    if cited_source_ids is not None:
        cited_bases = [_base_source_id(s) for s in cited_source_ids]
        cited_unique = set(cited_bases)
        if cited_unique:
            cite_p = sum(1 for s in cited_unique if s in expected) / len(cited_unique)
        if expected:
            cite_r = sum(1 for s in expected if s in cited_unique) / len(expected)

    return PerQuestionScore(
        qid=qid,
        question=question,
        expected_source_ids=sorted(expected),
        retrieved_source_ids=retrieved_bases,
        cited_source_ids=list(cited_source_ids) if cited_source_ids else [],
        recall_at_5=_recall_at(5),
        recall_at_10=_recall_at(10),
        reciprocal_rank=rr,
        citation_precision=cite_p,
        citation_recall=cite_r,
        latency_ms=latency_ms,
        model=model,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cache_read_input_tokens=cache_read_input_tokens,
        cache_creation_input_tokens=cache_creation_input_tokens,
        error=error,
    )


def aggregate(scores: list[PerQuestionScore]) -> MetricsSummary:
    """Aggregate per-question scores into a summary."""
    if not scores:
        return MetricsSummary(
            n_questions=0,
            recall_at_5=0.0, recall_at_10=0.0, mrr=0.0,
            citation_precision=None, citation_recall=None,
            claim_coverage=None, unsupported_claims_total=None,
            latency_p50_ms=None, latency_p95_ms=None,
            avg_input_tokens=None, avg_output_tokens=None,
            avg_cost_usd=None,
        )

    n = len(scores)
    r5 = sum(s.recall_at_5 for s in scores) / n
    r10 = sum(s.recall_at_10 for s in scores) / n
    mrr = sum(s.reciprocal_rank for s in scores) / n

    cite_p_vals = [s.citation_precision for s in scores if s.citation_precision is not None]
    cite_r_vals = [s.citation_recall for s in scores if s.citation_recall is not None]
    cite_p = sum(cite_p_vals) / len(cite_p_vals) if cite_p_vals else None
    cite_r = sum(cite_r_vals) / len(cite_r_vals) if cite_r_vals else None

    latencies = [s.latency_ms for s in scores if s.latency_ms is not None]
    p50 = int(statistics.median(latencies)) if latencies else None
    p95 = int(_percentile(latencies, 95)) if latencies else None

    in_tokens = [s.input_tokens for s in scores if s.input_tokens is not None]
    out_tokens = [s.output_tokens for s in scores if s.output_tokens is not None]
    avg_in = sum(in_tokens) / len(in_tokens) if in_tokens else None
    avg_out = sum(out_tokens) / len(out_tokens) if out_tokens else None

    costs = [
        c for c in (
            _cost(
                s.model, s.input_tokens, s.output_tokens,
                s.cache_read_input_tokens, s.cache_creation_input_tokens,
            )
            for s in scores
        )
        if c is not None
    ]
    avg_cost = sum(costs) / len(costs) if costs else None

    return MetricsSummary(
        n_questions=n,
        recall_at_5=r5, recall_at_10=r10, mrr=mrr,
        citation_precision=cite_p, citation_recall=cite_r,
        claim_coverage=None,            # populated only by LLM-judge path (Phase 8 stretch)
        unsupported_claims_total=None,
        latency_p50_ms=p50, latency_p95_ms=p95,
        avg_input_tokens=avg_in, avg_output_tokens=avg_out,
        avg_cost_usd=avg_cost,
        by_qid=[asdict(s) for s in scores],
    )


def _percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    sorted_vals = sorted(values)
    k = (len(sorted_vals) - 1) * (pct / 100.0)
    f = int(k)
    c = min(f + 1, len(sorted_vals) - 1)
    if f == c:
        return sorted_vals[f]
    return sorted_vals[f] + (sorted_vals[c] - sorted_vals[f]) * (k - f)


def score_run(results_path: Path, golden_path: Path) -> MetricsSummary:
    """Re-score a previously-run eval from JSONL on disk.

    Called by the post-run summary step and by Phase 7's evals tab when
    it loads ``.summary.json`` files.
    """
    golden = {}
    with golden_path.open(encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            rec = json.loads(line)
            golden[rec["qid"]] = rec

    scores: list[PerQuestionScore] = []
    with results_path.open(encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            row = json.loads(line)
            qid = row["qid"]
            gr = golden.get(qid, {})
            scores.append(score_question(
                qid=qid,
                question=gr.get("question", row.get("question", "")),
                expected_source_ids=gr.get("expected_source_ids", []),
                retrieved_source_ids=row.get("retrieved_source_ids", []),
                cited_source_ids=row.get("cited_source_ids"),
                latency_ms=row.get("latency_ms"),
                model=row.get("model"),
                input_tokens=row.get("input_tokens"),
                output_tokens=row.get("output_tokens"),
                cache_read_input_tokens=row.get("cache_read_input_tokens"),
                cache_creation_input_tokens=row.get("cache_creation_input_tokens"),
                error=row.get("error"),
            ))
    return aggregate(scores)
