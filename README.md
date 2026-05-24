# Graph

**An AI-powered operating manual for an HVAC parts distributor.**

Graph ingests messy real-world documents — manufacturer bulletins, regulatory
filings, supplier emails, internal SOPs, service tickets, ERP exports — and
turns them into a structured, citation-grounded knowledge base that a business
owner can query in natural language.

Portfolio piece demonstrating practical enterprise AI deployment: document
ingestion, hybrid retrieval, knowledge structuring, citation grounding,
workflow design, audit/trust, and evaluation.

---

## What it demonstrates

| Skill | Where it shows up |
| --- | --- |
| **Document ingestion** | 5 per-format loaders (markdown, email, JSONL tickets, CSV, PDF) under `src/ingest/loaders/`. Normalize → chunk → embed → index. |
| **Hybrid retrieval** | BM25 + vector cosine, min-max normalized, optional Voyage rerank. Filters push down to LanceDB. `src/retrieval/`. |
| **Citation grounding** | Every retrieved chunk gets a stable per-trace `cN` id. Final answers must cite `[cN]`; hallucinated ids are dropped. UI renders inline footnotes + a Citations panel per message. |
| **Knowledge structuring** | LLM-driven wiki builder synthesizes pages with `[chunk_id]` citations; stale pages auto-detected when sources change. `src/structure/`. |
| **Workflow design** | Four named ops-lead workflows (refrigerant exposure, supplier risk, tariff response, daily brief) with parameter schemas. `src/workflows/`. |
| **Audit + trust** | Every model call, tool call, and tool result is logged with a `trace_id`. "Show sources" surfaces the full trace per answer. |
| **Evals** | Hand-authored 30-question golden set; recall@5/@10, MRR, citation precision; surfaced in the Admin → Evals tab. `tests/eval/`, `src/eval/`. |

---

## Architecture

Four layers stacked on a fourth.

```
┌─ Sources ─────────────────────────────────────────────────────────┐
│ Real public PDFs (EPA, DOE) — fetched on demand                   │
│ Synthetic: manufacturer TSBs, internal SOPs, supplier emails,     │
│ service tickets, spec sheets. 86 manifest entries / 120 Documents │
└─────────────────────────┬─────────────────────────────────────────┘
                          ▼
        ┌────────────────────────────────────────┐
        │ Ingestion (src/ingest/)                │
        │ extract → chunk (recursive, heading-   │
        │ aware) → embed → metadata enrichment   │
        │ → index                                │
        └─────┬───────────────────────┬──────────┘
              ▼                       ▼
   ┌──────────────────┐    ┌────────────────────┐
   │ LanceDB + BM25   │    │ DuckDB             │
   │ chunk store      │    │ (orders, inventory,│
   │ (src/retrieval/) │    │ customers, …)      │
   └────────┬─────────┘    └─────────┬──────────┘
            │                        │
            ▼                        │
   ┌────────────────────────┐        │
   │ Structurer             │        │
   │ chunks → wiki pages    │        │
   │ + provenance + cites   │        │
   │ (src/structure/)       │        │
   └────────┬───────────────┘        │
            ▼                        │
   ┌──────────────────────────┐      │
   │ Markdown wiki            │      │
   │ data/wiki/               │      │
   └──────────┬───────────────┘      │
              │                      │
              └──────┬───────────────┘
                     ▼
        ┌────────────────────────────┐
        │ Agent loop (src/agent/)    │
        │ Tools: retrieve, read_     │
        │ source, read_wiki_page,    │
        │ run_sql, get_schema, …     │
        │ Per-trace citation reg.    │
        └────────────┬───────────────┘
                     ▼
        FastAPI (chat, workflows, admin, audit, briefs)
        Vanilla-JS UI: streaming chat, inline citations,
        sources panel, workflows drawer, admin tabs.
```

Three sources of truth, each behind a tool: **retrieve** (source corpus,
chunk-level citations), **wiki** (LLM-built structured knowledge), **SQL**
(operational facts in DuckDB).

---

## Evals

Run on a hand-authored 30-question golden set covering refrigerant
regulation, SOPs, supplier behavior, technical bulletins, and install
procedures. Ground truth at the **source level** so chunk-hash churn doesn't
break the golden records.

Three runs side-by-side show how each layer contributes:

| Mode | recall@5 | recall@10 | MRR | citation precision | citation recall | p50 latency | cost / query |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| BM25 only | 0.867 | 0.967 | 0.668 | — | — | 19 ms | $0 |
| Hybrid (BM25 + Voyage) | **0.967** | **1.000** | 0.752 | — | — | 235 ms | $0.0001 |
| **Agent loop** (Sonnet 4.6 + hybrid retrieval) | **0.967** | **1.000** | **0.950** | **0.708** | **0.983** | 21 s | $0.032 |

The agent's **0.983 citation recall** means it finds and cites 98% of
the sources the human curator marked as expected for each question. The
MRR jump from 0.752 → 0.950 reflects the agent re-issuing retrievals
with reformulated queries when the first pass doesn't surface the right
chunk.

Reproduce locally:

```bash
python scripts/run_evals.py                    # retrieval-only, free
python scripts/run_evals.py --mode agent       # agent mode, ~$1
```

Summary JSON lands in `data/evals/<run-id>.summary.json` and surfaces
in the Admin → Evals tab. The agent-mode run is pinned as a regression
baseline at [`tests/eval/baseline.summary.json`](tests/eval/baseline.summary.json).

---

## Quick start

```bash
# 1. Install
python -m venv .venv && source .venv/bin/activate
pip install -e .
# Optional: pip install -e .[voyage]   # enables hybrid retrieval

# 2. Configure
cp .env.example .env
# Edit .env to set ANTHROPIC_API_KEY. VOYAGE_API_KEY is optional —
# without it, the vector half of retrieval degrades to deterministic
# hash pseudo-vectors and BM25 carries the search.

# 3. Generate the synthetic source corpus + manifest
python scripts/generate_corpus.py

# 4. (Optional) Fetch real public regulatory PDFs as anchor inputs
python scripts/fetch_anchors.py

# 5. Ingest: chunks → embeddings → LanceDB + BM25
python scripts/ingest.py

# 6. Build the structured wiki (refrigerants, regulations, manufacturers,
#    procedures — 32 pages by default; existing skus/suppliers/customers
#    are template-rendered separately)
python scripts/build_wiki.py --health

# 7. Run the eval suite
python scripts/run_evals.py

# 8. Start the UI
uvicorn src.api.main:app --reload
# open http://127.0.0.1:8000
```

The UI has four entry points in the top bar:

- **Chat** (the main surface) — natural language Q&A with inline `[cN]`
  citations and a per-message Citations panel + "Show sources" audit trail.
- **Workflows** — refrigerant exposure, supplier risk, tariff response,
  daily brief. Each takes parameters and runs through the same agent loop.
- **Daily brief** — view the most recent standalone brief from
  `data/briefs/`.
- **Admin** — three tabs: Ingest (corpus browser), Knowledge health
  (orphans, thin pages, coverage by bucket), Evals (latest run summary).

---

## Layout

```
.
├── src/
│   ├── ingest/
│   │   ├── loaders/       # per-format loaders (md, email, ticket, csv, pdf)
│   │   ├── chunking.py    # heading-aware recursive chunker, tiktoken
│   │   ├── embed.py       # Voyage + hash-pseudo-vector fallback + cache
│   │   ├── metadata.py    # pattern + optional Haiku entity enrichment
│   │   ├── csv_loader.py  # legacy: ERP CSVs → DuckDB
│   │   └── synthetic.py   # synthetic ERP data generator
│   ├── retrieval/
│   │   ├── index.py       # writes LanceDB + rebuilds BM25
│   │   └── search.py      # hybrid retrieve() + read_source()
│   ├── structure/
│   │   ├── concepts.yaml  # declared ontology
│   │   ├── builder.py     # chunks → wiki page with citations
│   │   ├── freshness.py   # stale-page detection + rebuilds
│   │   └── health.py      # orphans / contradictions / coverage
│   ├── eval/
│   │   ├── runner.py      # retrieval-only + agent modes
│   │   └── metrics.py     # recall@k, MRR, citation precision/recall
│   ├── workflows/
│   │   ├── definitions.py # four named workflows + parameter schemas
│   │   └── runner.py      # validate + format + dispatch
│   ├── agent/             # hand-rolled tool-use loop, prompts, router
│   ├── tools/             # sql_query, wiki_read
│   ├── audit/             # SQLite append-only trace log
│   ├── api/               # FastAPI: chat, workflows, briefs, audit, admin
│   ├── compile/           # legacy templated wiki compiler
│   └── briefs/            # daily executive brief generator
├── data/
│   ├── sources/           # input corpus + manifest.yaml
│   ├── wiki/              # generated markdown wiki (Obsidian-compatible)
│   ├── raw/               # synthetic ERP CSVs (for DuckDB)
│   ├── evals/             # eval-run outputs (one per run)
│   ├── retrieval.lancedb/ # vector store
│   ├── bm25.pkl           # BM25 index
│   ├── staging.duckdb     # ERP-mirror tabular data
│   └── audit.sqlite       # agent-action trace log
├── web/                   # vanilla-JS chat UI (no build step)
├── scripts/               # pipeline drivers
│   ├── generate_corpus.py
│   ├── fetch_anchors.py
│   ├── ingest.py
│   ├── build_wiki.py
│   ├── run_evals.py
│   ├── generate_synthetic_data.py
│   ├── run_full_pipeline.py    # legacy template compiler
│   └── generate_brief.py
└── tests/
    └── eval/golden.jsonl   # 30 hand-authored eval questions
```

---

## Key decisions (and where they're written up)

Detailed in [`implementation-notes.html`](implementation-notes.html). Highlights:

- **Local-first stack.** LanceDB embedded (no server), in-process BM25,
  SQLite caches, SQLite audit. The whole system runs from a clone with no
  infra.
- **Graceful degradation when API keys are missing.** Voyage absent →
  hash-pseudo-vectors + a loud warning, BM25 carries retrieval. Anthropic
  absent → structurer deterministic-mode falls back to snippet layout
  instead of LLM synthesis. The pipeline runs end-to-end either way.
- **No agent framework.** ~250-line hand-rolled loop. Tools dispatch via a
  dict; citations come from a per-trace registry.
- **Citations at the source level, not the chunk level**, for evals and
  freshness — chunk_ids are content-hashed so they're not stable golden-set
  identifiers.
- **Source corpus is auto-built from frontmatter and sidecars**, not
  hand-edited. Adding a source means dropping a file into the right bucket;
  `scripts/generate_corpus.py` rebuilds `manifest.yaml` from a tree walk.

The companion file [`followups.html`](followups.html) tracks every item I
explicitly deferred — what it is, why it's deferred, what triggers it.

---

## Obsidian config handling

The generated wiki under `data/wiki/` is an Obsidian-compatible vault.
Obsidian rewrites its own config files when you open the vault, so:

- Canonical defaults live in `data/obsidian-defaults/` (tracked).
- Per-machine config lives in `data/wiki/.obsidian/` (gitignored).
- The pipeline calls `src/compile/obsidian.py::setup_obsidian()` to seed
  defaults; it never overwrites your tweaks.

Reset to shipped defaults:

```bash
python scripts/setup_obsidian.py --force
```
