# Graph MVP

LLM-native operational intelligence for PE-backed HVAC parts distributors.
Synthetic HVAC distributor data → living markdown wiki + DuckDB → natural-language
chat with full audit traces.

See `../graph-strategy.md`, `../graph-mvp-sketch.md`, and `../graph-market-analysis.md`
for product context. See `PLAN.md` for the implementation plan.

## Quick start

```bash
# 1. Install
python -m venv .venv && source .venv/bin/activate
pip install -e .

# 2. Configure
cp .env.example .env
# edit .env to set ANTHROPIC_API_KEY

# 3. Generate synthetic data and compile the wiki
python scripts/generate_synthetic_data.py
python scripts/run_full_pipeline.py

# Optional: have Claude write narrative + substitute lists for the first
# 100 SKU pages (cached in data/narrative_cache.sqlite, so re-runs are free)
python scripts/run_full_pipeline.py --enrich-sku-limit 100
# ...or pass -1 to enrich every SKU.

# 4. Browse the wiki in Obsidian
#    Open the vault at: data/wiki/

# 5. Start the chat UI
uvicorn src.api.main:app --reload
# open http://127.0.0.1:8000

# 6. Optional: generate today's executive brief (requires API key)
python scripts/generate_brief.py
# Brief lands at data/briefs/<today>.md and is viewable via the
# "Daily brief" button in the UI.
```

## Layout

- `src/ingest/` — CSV/PDF/synthetic data loaders → DuckDB
- `src/compile/` — DuckDB → markdown wiki (LLM-templated pages)
- `src/agent/` — agent loop, tool definitions, prompts
- `src/tools/` — `read_wiki_page`, `run_sql`, etc. (functions the agent calls)
- `src/audit/` — append-only trace log (SQLite)
- `src/api/` — FastAPI chat backend
- `data/wiki/` — the Obsidian-compatible markdown vault (generated)
- `data/staging.duckdb` — mirrored ERP tables (generated)
- `data/audit.sqlite` — agent action traces (generated)
- `web/` — minimal chat frontend
- `scripts/` — one-shot pipeline runners and demo helpers
