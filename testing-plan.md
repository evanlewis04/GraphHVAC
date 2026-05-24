# Live Testing Plan

End-to-end validation pass once `ANTHROPIC_API_KEY` is set. Designed to
exercise every layer that couldn't be tested without a live model, at
the lowest defensible cost.

---

## TL;DR cost

**Estimated total: $4–6** with the recommended model selection (Sonnet
4.6 across the board, Haiku 4.5 for cheap enrichment).

If you leave the current `GRAPH_AGENT_MODEL=claude-opus-4-7` configured,
the agent-heavy phases (A, B, C, E, H) cost ~5× more — total ~**$20–25**.
**Recommended:** switch agent to Sonnet 4.6 for the test pass; revisit if
quality is insufficient.

| Phase | What | Cost (Sonnet) | Cost (Opus) |
| --- | --- | --- | --- |
| A | Smoke chat × 5 | $0.30 | $1.50 |
| B | 4 workflows | $0.60 | $3.00 |
| C | Citation rendering × 3 | $0.20 | $1.00 |
| D | Admin tabs (UI only) | $0.00 | $0.00 |
| E | Agent-mode eval (30 questions) | $2.50 | $12.50 |
| F | Structurer LLM rebuild (32 pages) | $1.00 | n/a (Sonnet only) |
| G | Health contradiction check | $0.15 | n/a (Sonnet only) |
| H | Daily brief generator | $0.10 | $0.50 |
| I | Haiku metadata enrichment (opt) | $0.10 | n/a (Haiku only) |
| — | Voyage embeddings + reranks | $0.05 | $0.05 |
| **Total** | | **~$5** | **~$19** |

---

## Model selection (and why)

The current `.env` is leftover MVP configuration. For this test pass, use:

| Task | Recommended model | Why |
| --- | --- | --- |
| **Agent loop** (chat + workflows + eval mode) | **Sonnet 4.6** | Tool-use loops don't benefit much from Opus over Sonnet, and the cost ratio is 5×. Sonnet handles multi-step retrieve→SQL→synthesize patterns reliably at this task scale. |
| **Structurer** (`build_wiki.py`) | **Sonnet 4.6** | One-shot synthesis from retrieved chunks. Already configured via `GRAPH_COMPILER_MODEL`. |
| **Daily brief** (`generate_brief.py`) | **Sonnet 4.6** | Same as structurer — one structured document from data + sources. |
| **Health contradictions** (opt-in via `--health-llm`) | **Sonnet 4.6** | Multi-page reasoning, but small per-call. Sonnet is right-sized. |
| **Metadata enrichment** (opt-in via `--llm-enrich`) | **Haiku 4.5** | Cheap entity extraction over many small chunks. Haiku is the right tool. Already the default in `src/ingest/metadata.py`. |

To switch the agent model for the test pass, edit `.env`:

```diff
- GRAPH_AGENT_MODEL=claude-opus-4-7
+ GRAPH_AGENT_MODEL=claude-sonnet-4-6
```

Restart the uvicorn process to pick up the change.

---

## Pricing assumptions (mid-2026, approximate)

| Model | Input / 1M | Output / 1M | Cache reads / 1M |
| --- | --- | --- | --- |
| Sonnet 4.6 | $3.00 | $15.00 | $0.30 (10%) |
| Opus 4.7 | $15.00 | $75.00 | $1.50 (10%) |
| Haiku 4.5 | $0.80 | $4.00 | $0.08 (10%) |
| Voyage-3 embeddings | $0.18 | — | — |
| Voyage rerank-2 | $0.05 per 1k searches | — | — |

The agent loop already uses Anthropic prompt caching on the system
prompt + tool schemas (`src/agent/loop.py` sets `cache_control:
ephemeral`), so iterations 2+ within a query reuse cached context at 10%
of the input cost. The estimates below assume the cache hits.

---

## Phases

### Phase A — Smoke chat (5 minutes, ~$0.30)

**Goal:** confirm the agent loop, tool registration, and citation
rendering end-to-end on the simplest path.

**Test:** run each of the 4 suggested questions from the UI's empty
state, plus one ad-hoc question:

1. "What's our exposure to the R-410A phase-out, and which 5 customers are most affected?"
2. "Show me suppliers we depend on for more than 20% of a single category."
3. "Top 5 customers by revenue, with their segment and region."
4. "How many capacitors do we stock at the Atlanta warehouse?"
5. Ad-hoc: "What did the Carrier March 2025 tariff email say about coil pricing?"

**Success criteria:**
- Each query returns a final answer.
- Audit trail (Show sources) shows tool calls in sensible order.
- At least 3 of the 5 answers contain `[cN]` citations.
- Citations panel populates beneath the answer.
- Each query completes in ≤30 seconds with Sonnet.

**Token estimate:** ~5–8k input (cached) + ~1k output per query × 5 = ~$0.06 each → **~$0.30**.

---

### Phase B — Workflows (10 minutes, ~$0.60)

**Goal:** confirm each named workflow runs the recipe and produces the
structured output described in its template.

**Test:** open the Workflows drawer, run each:

1. **Refrigerant exposure analysis** with refrigerant=R-410A, top_n=10
2. **Supplier risk review** with supplier="Lennox PartsPlus", manufacturer="Lennox"
3. **Tariff response** with manufacturer="Carrier", magnitude_pct=4.2, category="Condenser"
4. **Daily executive brief** (no parameters)

**Success criteria:**
- Each workflow produces all H2 sections specified in its prompt.
- SQL queries appear inline in code blocks (refrigerant + supplier + tariff workflows).
- Citations panel shows ≥3 cited sources for refrigerant + tariff + brief.
- "Workflow · {title}" appears as the user message in chat.

**Token estimate:** workflows are heavier than chat queries (more
iterations, more retrieves). ~10–15k cached input + ~2k output each →
~$0.15 each → **~$0.60**.

---

### Phase C — Citation UX (5 minutes, ~$0.20)

**Goal:** validate Phase 4 + Phase 7 citation UI affordances.

**Test:** pick 3 answers from Phase A/B that have ≥4 citations and:

1. **Hover** each `[cN]` link → custom popover appears with snippet
2. **Click** each `[cN]` link → scrolls to citation card, flashes yellow
3. **Click "Open source"** on a citation card → expands raw source text
4. **Click "Open source"** again → collapses

If Phase A/B answers already covered these, no new queries needed.
Otherwise, ask one more question that touches multi-source data:
"Compare what the AIM Act, R-410A timeline doc, and R-454B overview say
about the 2025 GWP cutoff." (~$0.10)

**Success criteria:**
- Popover styled (dark theme, source_id + heading + snippet)
- Click-to-scroll works on all citation badges
- Open-source button loads + collapses + reloads from cache

---

### Phase D — Admin tabs (5 minutes, $0)

**Goal:** validate the three admin tabs render with real data.

**Test:** Admin button → cycle through tabs:

1. **Ingest tab:** 86 sources, 117 chunks, last_indexed timestamps populated
2. **Knowledge health tab:** 32 pages, coverage tiles + per-bucket table render, thin pages list visible
3. **Evals tab:** retrieval-only run from the existing pre-test eval populates (recall@5 = 0.867)

**Success criteria:**
- No 500 errors in browser console
- Tab switching is instant (data already cached in admin endpoint responses)
- "Open source" buttons on Ingest tab (if implemented later) work

**Cost: $0** — admin endpoints don't hit the model.

---

### Phase E — Agent-mode eval (15 minutes, ~$2.50)

**Goal:** fill in `citation_precision` + `citation_recall` columns the
retrieval-only eval can't measure. Confirm the agent's citation
discipline holds across the golden set.

**Test:**

```bash
./.venv/Scripts/python scripts/run_evals.py --mode agent
```

**Success criteria:**
- All 30 questions complete without errors.
- `recall@5` ≥ 0.85 (matches or beats retrieval-only baseline).
- `citation_precision` ≥ 0.70 (model rarely cites non-expected sources).
- `citation_recall` ≥ 0.60 (model cites at least one expected source per question).
- Average latency per query ≤ 20 seconds.
- Run summary lands at `data/evals/<run-id>-agent.summary.json`.
- New run appears in Admin → Evals tab.

**Token estimate:** each agent run averages ~12k cached input + ~1.5k
output → ~$0.08 per question × 30 = **~$2.50**.

If you upgrade to hybrid retrieval with Voyage first (recommended), the
retrieval baseline should lift before this measurement.

---

### Phase F — Structurer LLM rebuild (10 minutes, ~$1)

**Goal:** validate Phase 5's LLM synthesis path (currently every page is
the deterministic stub). Produces real prose with `[chunk_id]` inline
citations across the 32 structurer-owned pages.

**Test:**

```bash
./.venv/Scripts/python scripts/build_wiki.py --force
```

The `--force` bypasses the structure cache so we rebuild every page
through Sonnet (not the deterministic fallback).

**Success criteria:**
- All 32 pages rebuild without errors.
- Spot-check `data/wiki/refrigerants/r-410a.md`: opens with prose synthesis (not the "_assembled without LLM_" banner), required sections present, every paragraph has at least one `[chunk_id]` citation.
- Frontmatter `synthesizer: llm` (not `deterministic`).
- No `validation_warnings` for the majority of pages.

**Token estimate:** ~6.5k input + 800 output per page × 32 pages → ~$0.03 per page → **~$1**.

---

### Phase G — Health contradiction check (5 minutes, ~$0.15)

**Goal:** validate the optional LLM contradiction detection in
`structure/health.py`.

**Test:**

```bash
./.venv/Scripts/python scripts/build_wiki.py --rebuild-stale --health --health-llm
```

(`--rebuild-stale` will be a no-op right after Phase F; `--health-llm`
adds the contradiction pass.)

**Success criteria:**
- Health-check report at `data/wiki/concepts/health-check.md` includes an
  "LLM contradiction findings" section.
- Sonnet either finds contradictions (and they're plausible, not
  hallucinated) OR reports "NONE" cleanly per entity type.
- Admin → Knowledge health tab shows the contradictions count.

**Token estimate:** 4 LLM calls (one per entity type), ~10k input + ~500
output each → ~$0.04 per call → **~$0.15**.

---

### Phase H — Daily brief standalone (5 minutes, ~$0.10)

**Goal:** confirm the standalone brief generator (separate from the
workflow path) writes a real artifact.

**Test:**

```bash
./.venv/Scripts/python scripts/generate_brief.py
```

**Success criteria:**
- File appears at `data/briefs/YYYY-MM-DD.md`.
- All four sections (refrigerant exposure, top customers, supplier
  concentration, inventory health) are populated.
- File contains `[cN]` citations.
- Daily-brief drawer in the UI shows it under the most recent date.

**Token estimate:** ~12k cached input + 1.5k output → **~$0.10**.

---

### Phase I — Haiku metadata enrichment (optional, ~$0.10)

**Goal:** validate the LLM enrichment path in `src/ingest/metadata.py`
(default uses pattern matching only).

**Test:**

```bash
./.venv/Scripts/python scripts/ingest.py --drop-first --llm-enrich --skip-anchors
```

Re-ingests the full corpus with Haiku-enriched metadata on every chunk.

**Success criteria:**
- ~120 chunks re-indexed.
- Spot-check a chunk via `/admin/source/{source_id}`: metadata includes
  `mentioned_*` fields populated.
- Cache hits on second run (instant re-ingest, $0).

**Token estimate:** 120 chunks × ~500 input + ~100 output → ~$0.10
Haiku.

---

## Pre-test checklist

Before starting, confirm:

- [ ] `ANTHROPIC_API_KEY=sk-ant-...` (real key, not placeholder)
- [ ] `GRAPH_AGENT_MODEL=claude-sonnet-4-6` (or accept the ~5× cost)
- [ ] Optional: `VOYAGE_API_KEY=...` + `pip install -e .[voyage]`
      (lifts retrieval quality for Phase A/B/C/E)
- [ ] `python scripts/ingest.py` has been run (LanceDB + BM25 populated)
- [ ] `python scripts/build_wiki.py --no-llm` has been run (32 pages present)
- [ ] UI starts: `uvicorn src.api.main:app --reload` → http://127.0.0.1:8000

If Voyage is added between Phase D and E, re-run Phase E to capture the
lift; otherwise compare BM25-only vs hybrid in a single side-by-side later.

---

## Watch list (most likely failure points)

| Symptom | Likely cause |
| --- | --- |
| Agent ignores `retrieve` tool, only uses wiki+SQL | System prompt update didn't land — confirm Phase 4 prompt is in `src/agent/prompts.py` |
| `[cN]` rendered as plain text | Markdown renderer escaped brackets before `decorateCitations` ran |
| Workflow output skips required sections | Sonnet undershot the prompt — bump `max_tokens` or tighten template instructions |
| Latency > 60 s per query | Agent is looping; check audit trail for repeat tool calls |
| Citation precision < 0.5 in Phase E | Model is over-citing — tighten "only cite ids you've seen" in system prompt |
| Structurer pages still show "deterministic" after Phase F | LLM call failed silently; check stderr for `[structure] LLM call failed` |
| Health contradiction report says "NONE" for everything | Either no contradictions exist (likely) or sample size per type is too small |

---

## After the test pass

- Capture final eval summary path and commit it under `tests/eval/baseline.summary.json` (closes the "baseline + pytest regression" followup).
- Record 30–60 second demo GIF from Phase B (closes the "demo GIF for README" followup).
- Update `followups.html` to resolve the "End-to-end agent run" item and any others that the test pass closed.
- Update the README's eval table with the agent-mode numbers from Phase E.

---

## Notes on cost variance

Estimates assume Anthropic prompt caching works as designed. Real-world
costs may swing **±30%** based on:

- How many tool-call iterations each query takes (model judgment)
- Whether the model writes verbose explanations or terse answers
- Whether the 5-minute cache TTL is hit (back-to-back queries help)

If costs run higher than estimated, the agent is likely doing extra
tool calls — surface this by inspecting the audit trail for repeat
retrieves on similar queries.
