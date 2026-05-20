# Graph — Implementation Plan

Working plan for **Graph**, an AI-powered operating manual for an HVAC parts
distributor. Built as a portfolio piece demonstrating practical enterprise AI
deployment: document ingestion, hybrid retrieval, citation grounding, structured
knowledge generation, evals, and workflow design.

The plan layers on top of the existing MVP (templated wiki + agent loop + SQL
tooling + audit log + FastAPI/UI). Phase numbers are the unit of progress.

---

## Architecture target

```
┌─ Sources ─────────────────────────────────────────────────────────┐
│ PDFs (manuals, bulletins, SDS)   Markdown SOPs    Service tickets │
│ Emails / transcripts              CSV ops data    Spec sheets     │
└─────────────────────────┬─────────────────────────────────────────┘
                          ▼
        ┌────────────────────────────────────────┐
        │ Ingestion pipeline                     │
        │ extract → normalize → chunk → embed    │
        │ → metadata enrich → index              │
        └─────┬───────────────────────┬──────────┘
              ▼                       ▼
   ┌──────────────────┐    ┌────────────────────┐
   │ Vector + BM25    │    │ DuckDB (ops facts) │
   │ chunk store      │    │ existing           │
   └────────┬─────────┘    └─────────┬──────────┘
            │                        │
            ▼                        │
   ┌────────────────────────┐        │
   │ Knowledge structurer   │        │
   │ chunks → wiki pages    │        │
   │ + provenance links     │        │
   └────────┬───────────────┘        │
            ▼                        │
   ┌──────────────────────────┐      │
   │ Markdown wiki (existing) │      │
   └──────────┬───────────────┘      │
              │                      │
              └──────┬───────────────┘
                     ▼
        ┌────────────────────────────┐
        │ Agent loop (existing)      │
        │ Tools: retrieve, read_wiki,│
        │ run_sql, list_dir, search  │
        │ + chunk-level citations    │
        └────────────┬───────────────┘
                     ▼
        FastAPI + UI with sources pane, workflows,
        eval dashboard, audit trace (existing)
```

---

## Locked decisions

- **Business domain:** HVAC parts distributor (keep current ontology).
- **Primary user persona:** business owner / ops lead.
- **Source strategy:** synthetic-but-realistic corpus with 3–6 real public
  regulatory / manufacturer anchors.
- **Retrieval stack:** local-first — LanceDB for vector store, in-process
  BM25 (`rank_bm25`), Voyage embeddings (`voyage-3` or `voyage-3-lite`),
  optional Voyage `rerank-2` on top-N.
- **Model routing:** Haiku 4.5 for ingest metadata + structurer drafts +
  retrieval-heavy single-hop queries; Sonnet/Opus for multi-step workflows.

---

## Phases

### Phase 1 — Reframe + scaffolding (1–2 days)

- Rewrite `README.md`, `graph-strategy.md`, `PLAN.md` around the new positioning.
- Add module skeletons: `src/ingest/loaders/`, `src/ingest/chunking.py`,
  `src/ingest/embed.py`, `src/ingest/metadata.py`, `src/retrieval/`,
  `src/structure/`, `src/eval/`.
- Define `data/sources/manifest.yaml` schema and lay out the
  `data/sources/{manuals,bulletins,sops,tickets,emails,specs}/` directory tree.

**Done when:** new architecture is documented, every new module imports cleanly,
lint clean.

### Phase 2 — Source corpus (2–3 days)

Curate ~80–120 mixed-format documents.

- **Real public anchors** (3–6 docs): manufacturer install manuals, EPA AIM
  Act bulletins, SDS sheets, AHRI standard summaries. Checked in only if
  redistribution is permitted; otherwise pulled by `scripts/fetch_anchors.py`.
- **Synthetic, deliberately messy:** supplier email threads, internal SOPs,
  manufacturer technical bulletins, service notes from contractor customers,
  supplier spec sheets, synthetic ERP exports.
- `data/sources/manifest.yaml` registers every doc with `source_id`, `path`,
  `type`, `expected_metadata`, `license`.

**Done when:** manifest validates and points at on-disk files; corpus mirrors
real distributor messiness.

### Phase 3 — Ingestion pipeline (3–4 days)

- `src/ingest/loaders/*.py` — one file per format, all emit a normalized
  `Document(source_id, content, metadata)`.
- `src/ingest/chunking.py` — recursive heading→paragraph chunker, 600–1000
  tokens, 100 overlap, heading path preserved.
- `src/ingest/metadata.py` — LLM-assisted enrichment (Haiku) for entities
  mentioned (SKUs, refrigerants, manufacturers, regulations); cached.
- `src/ingest/embed.py` — Voyage-3 embeddings; SQLite content-hash cache.
- `src/retrieval/index.py` — write chunks + embeddings to LanceDB; parallel
  in-process BM25 index.
- `scripts/ingest.py --manifest data/sources/manifest.yaml` — idempotent driver.
- Audit-log every ingest run.

**Done when:** ingest on the full corpus produces a queryable LanceDB chunk
store; every chunk has `(source_id, chunk_id, page/line range, heading path)`
provenance.

### Phase 4 — Hybrid retrieval + new tools (2–3 days)

- `src/retrieval/search.py` — `retrieve(query, k, filters)` returning ranked
  chunks. Hybrid score (weighted BM25 + cosine), optional Voyage `rerank-2`
  on top-N.
- Filters: doc type, manufacturer, refrigerant, date range, source_id.
- New agent tools in `src/agent/tools.py`: `retrieve`, `read_source`.
- Loop captures every `citation_id` referenced in the final answer; API
  returns `{answer, citations: [...], trace_id, iterations}`.
- Inline `[c1]`, `[c2]` citation rendering in UI.

**Done when:** a representative question returns an answer with 3–5 cited
chunks; sources panel renders them; audit trace shows chunk-level events.

### Phase 5 — Knowledge structurer (3–5 days)

The differentiator from a plain RAG chatbot.

- `src/structure/concepts.yaml` — declares target wiki ontology: SKUs,
  suppliers, customers, refrigerants, regulations (new), procedures (new),
  manufacturers (new), concept pages.
- `src/structure/builder.py` — for each declared entity: retrieve chunks →
  LLM synthesizes a wiki page with inline `[chunk_id]` citations → validate
  → write to `data/wiki/...` with frontmatter `source_chunks: [...]`,
  `last_built`, `template_version`.
- `src/structure/freshness.py` — re-ingesting an updated source marks
  dependent pages stale; rebuild on demand or via `--rebuild-stale`.
- `src/structure/health.py` — periodic LLM pass for contradictions, orphan
  chunks, thin coverage, suggested new pages.

**Done when:** wiki regenerates from sources end-to-end; every wiki claim
traces back to a source chunk; re-ingesting an updated PDF regenerates the
affected pages.

### Phase 6 — Ops-lead workflows (2–3 days)

Named workflow entry points in the UI, each backed by the agent with
workflow-specific prompts + structured outputs.

- **Refrigerant exposure analysis** — pick a refrigerant → affected customers,
  revenue, retrofit guidance, regulatory citations.
- **Supplier risk review** — pick a supplier → concentration, recent bulletins,
  substitute coverage.
- **Tariff / price-change response** — manufacturer + magnitude → exposure,
  customer impact, recommended response.
- **Daily executive brief** — existing, regrounded in cited sources.

### Phase 7 — UI polish (2 days)

- Sources panel: ranked chunks with score, snippet, expand-to-page.
- Inline citations with hover preview.
- "Ingest" tab: corpus browser (every source doc, type, ingest date, chunk count).
- "Knowledge health" tab: wiki freshness grid, contradictions, coverage gaps.
- "Evals" tab: latest metrics + golden-set browser.

### Phase 8 — Evals + writeup (2–3 days)

- `tests/eval/golden.jsonl` — 30–50 hand-authored questions with ground-truth
  `source_id` + `chunk_id` lists + expected entity mentions.
- `scripts/run_evals.py` — retrieval (recall@5, recall@10, MRR), answer
  (citation precision, claim coverage via LLM-judge, unsupported-claim count),
  latency p50/p95, cost per query.
- Portfolio README: architecture diagram, decisions, evals table, demo GIF/video,
  deployment notes.

---

## What survives from the original MVP

**Keep:**
- Agent loop (`src/agent/loop.py`), SSE streaming, audit logger.
- Wiki + DuckDB hybrid pattern, Jinja templates, Obsidian config handling.
- FastAPI app + UI shell, daily brief generator (regrounded in Phase 5).
- Synthetic ops data generator.

**Change:**
- `src/ingest/` shifts from CSV-only to multi-format document ingestion.
- Tools surface gains `retrieve` and `read_source`.
- `src/ingest/pdf_parser.py` stub gets a real implementation in Phase 3.
- `src/agent/router.py` no-op becomes real model routing in Phase 4.
- Wiki page generation switches from templated-narrative to retrieval-grounded.

**Cut / rewritten:**
- PE-flavored concept pages and brief prompts.
- Hardcoded SKU substitute logic — replaced by retrieval-grounded substitutes.

---

## Timeline

~14–18 focused days. Phases 1–4 is the minimum viable demo (~8 days).
Phases 5–8 take it to portfolio-grade.
