# Graph — Strategy (one-pager)

**Graph** is an AI-powered operating manual for an HVAC parts distributor.
It demonstrates the full enterprise-AI-deployment stack on a single, vivid
domain: messy real-world documents become a structured, citation-grounded
knowledge base that a business owner can query in natural language.

## What it does

1. **Ingests messy source material** — manufacturer manuals (PDF), regulatory
   bulletins, supplier email threads, internal SOPs, service tickets, ERP
   exports. Normalizes them into a chunked, embedded knowledge corpus with
   stable provenance (every chunk traces back to a page in a source doc).
2. **Builds a structured wiki on top.** An LLM-driven structurer pulls
   chunks per declared entity (SKU, supplier, customer, refrigerant,
   regulation, procedure, manufacturer) and synthesizes a wiki page whose
   every claim cites a chunk. Pages mark themselves stale when the underlying
   source changes and regenerate.
3. **Answers business questions with citations.** A hand-rolled agent loop
   reads the wiki, retrieves chunks via hybrid (vector + BM25) search, and
   runs SQL against operational data in DuckDB. Every answer renders inline
   citations linking back to source chunks and source documents.
4. **Drives ops workflows.** Pre-built workflow lanes for refrigerant
   exposure analysis, supplier risk review, tariff / price-change response,
   and the daily executive brief — each producing structured, cited output.

## Architecture, in one paragraph

Three layers stacked on a fourth. **Knowledge** lives in a markdown wiki
(LLM-generated from source chunks, Obsidian-compatible, browseable). **Facts**
live in DuckDB (orders, inventory, customers — high-volume tabular data).
**Retrieval** lives in LanceDB + an in-process BM25 index over the raw source
chunks. Underneath them all, the **agent layer** is a hand-rolled tool-use
loop (no framework) that decides per question which surface to query. Every
model call and tool call writes to a SQLite audit log; every answer renders
the trace on demand.

## Why this architecture

- **Wiki + facts + retrieval as parallel layers** mirrors the actual shape of
  operational knowledge. Some questions are about relationships
  (substitutes, exposure, who-buys-what — wiki). Some are about precise
  numbers (totals, counts, history — SQL). Some are about reading the
  source of truth verbatim (regulatory text, manufacturer specs —
  retrieval). One layer alone is the wrong tool for ⅔ of the questions.
- **LLM-structured wiki + LLM-driven retrieval is the 2025 answer** to the
  problem older systems solved with hand-built knowledge graphs and rigid
  ETL pipelines. Faster to build, handles messy real-world inputs natively,
  and the LLM does the structuring work that used to be human-quarter scale.
- **Audit trail solves the trust problem** that always shows up around LLM
  systems for non-developer users. Every answer is decomposable to the
  exact files and queries that produced it.

## Primary user

Business owner / ops lead at a mid-market HVAC parts distributor — someone
who oversees inventory, supplier relationships, customer concentration, and
regulatory exposure across one or more warehouses. The product surfaces the
information they currently chase down across PDFs, spreadsheets, emails,
and ERP screens.

## What this project demonstrates

Practical enterprise-AI deployment skills end to end:

- **Document ingestion** from messy real-world formats (PDF, email, ticket,
  markdown, CSV).
- **Hybrid retrieval** combining lexical (BM25) and semantic (vector) search
  with optional reranking.
- **Citations and source grounding** at the chunk level — every claim is
  defensible.
- **Knowledge structuring** — turning ingestion output into a navigable,
  refreshable wiki rather than just stuffing chunks into a chatbot context.
- **Workflow design** — making the system useful for specific
  business-owner tasks, not just open-ended chat.
- **Evals** — measurable retrieval and answer quality on a hand-authored
  golden set.
- **Audit + trust** — every model call and tool call traced, every answer
  decomposable.

See [`PLAN.md`](PLAN.md) for the implementation plan and
[`README.md`](README.md) for setup.
