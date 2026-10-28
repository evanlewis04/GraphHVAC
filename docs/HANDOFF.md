# Continue Graph HVAC on another machine

The application, source corpus, three regulatory anchor PDFs, structured wiki
examples, tests, and deployment configuration are tracked in Git. The July 2026
evaluation files are preserved in [the historical archive](evals/20260726/README.md).
The README cost correction from PR #12 is included in this branch.

## Clone and install

```bash
git clone --branch chore/project-handoff https://github.com/evanlewis04/GraphHVAC.git
cd GraphHVAC
python -m venv .venv
```

On macOS/Linux:

```bash
source .venv/bin/activate
python -m pip install -e ".[dev]"
cp .env.example .env
```

On Windows PowerShell, activation is unnecessary:

```powershell
./.venv/Scripts/python.exe -m pip install -e ".[dev]"
Copy-Item .env.example .env
$env:PYTHONUTF8 = "1"
```

For the commands below, Windows users can replace `python` with
`./.venv/Scripts/python.exe`. Run all commands from the repository root.

## Configuration

- Set `ANTHROPIC_API_KEY` in your local `.env` for chat, workflows, briefs,
  and optional LLM wiki synthesis. Leave it blank for the offline setup below.
- For real vector embeddings, install `.[dev,voyage]` and add
  `VOYAGE_API_KEY` to `.env` before ingestion. Without it, retrieval uses the
  deterministic fallback; this does not reproduce the historical hybrid scores.
- Review `GRAPH_AGENT_MODEL` and `GRAPH_COMPILER_MODEL` for your API account.
  The checked-in example uses `claude-sonnet-5`; the prior hosted Haiku setting
  was a deployment override, not a change to the local defaults. To reproduce
  that choice, set `GRAPH_AGENT_MODEL=claude-haiku-4-5` explicitly.
- `.env` overrides shell variables in `src/config.py`. Restart the application
  after editing it. The eval CLI's `--model` flag explicitly overrides the model.
- Local auth is disabled unless both `DEMO_BASIC_AUTH_USER` and
  `DEMO_BASIC_AUTH_PASS` are configured. Configure them before exposing the app.

Secrets are intentionally absent from Git. Re-enter them on the new machine
using your secret store; neither the existing `.env` nor hosted credentials are
part of this handoff.

## Rebuild generated data

The operational database, raw ERP CSVs, vector/BM25 indexes, caches, and audit
history are local files ignored by Git. The first two commands below rebuild
the SQL data and templated wiki; ingestion alone does not create DuckDB.

```bash
python scripts/generate_synthetic_data.py
python scripts/run_full_pipeline.py
python scripts/ingest.py
python scripts/build_wiki.py --no-llm --health
python scripts/run_evals.py
python -m pytest -q
python -m uvicorn src.api.main:app --reload
```

Open <http://127.0.0.1:8000>. Chat, workflows, and brief generation require a
working Anthropic key. The commands above rebuild the corpus without Anthropic
calls; Voyage ingestion/retrieval uses paid APIs if its key is configured.
The tokenizer may download its public encoding table on first use.

Use the committed corpus and manifest for this setup. `generate_corpus.py`
is an optional corpus-authoring tool and currently contains older anchor URLs;
running it would replace the corrected manifest. The anchor PDFs are already
checked in, so `fetch_anchors.py` is unnecessary for a normal clone.

Regeneration rewrites generated wiki examples and may show Git diffs. Keep
intentional content changes separate from setup outputs. To change embedding
providers later, rebuild the index and use a fresh embedding cache; the cache
key does not distinguish fallback vectors from real vectors of the same model.

## What this handoff does not claim

- Old evaluation scores describe their recorded models, corpus, and dates;
  they are not a fresh answer-quality evaluation. Some July runs are subsets
  or interrupted runs. The pinned baseline remains unchanged.
- The original checkout's `data/wiki/_test_enriched/` is a generated test
  scratch tree. It remains local and is unnecessary to run the application.
- Historical chat/audit traces and generated briefs are not transferred by
  cloning. The preserved JSONL evaluations contain their recorded answers.
- `followups.html` retains deferred product ideas; this handoff does not
  turn those ideas into shipped features.
- No hosted deployment is performed by this handoff. The current Dockerfile
  copies local `data/`, so rebuild data before building an image. `fly.toml`
  names the existing demo app; deploying it would update that app.

Implementation references: [configuration](../src/config.py),
[ERP pipeline](../scripts/run_full_pipeline.py),
[ingestion](../scripts/ingest.py), [wiki build](../scripts/build_wiki.py),
[eval CLI](../scripts/run_evals.py), [ignored data](../.gitignore),
[Dockerfile](../Dockerfile).

## Handoff validation, 2026-10-28

Validated in a separate fresh Git worktree using the existing Python 3.13
environment's installed dependencies, with no copied `.env` or databases:

- Full test suite: **59 passed** after fixing one Windows test to read generated
  UTF-8 wiki files explicitly. One Starlette/httpx deprecation warning remains.
- ERP rebuild: 4,998 SKUs, 20 suppliers, 500 customers, 82,147 order lines,
  and 16,480 inventory rows.
- Ingestion: all 86 sources processed, 120 documents, 270 chunks, none skipped.
- Deterministic wiki rebuild: 32 structured pages. Health reports 148 orphan
  chunks, nine thin pages, and 43 dangling links; this fallback is a runnable
  starting point, not a claim of complete knowledge coverage.
- Thirty-question offline retrieval smoke: recall@5 0.867, recall@10 0.933,
  MRR 0.674. [Recorded outputs](evals/20261028/handoff-offline-smoke.summary.json)
  are separate from the historical hybrid baseline.
- In-process HTTP smoke: `/`, `/app.js`, `/pitch-brief.md`, `/workflows`,
  `/admin/sources`, and `/admin/evals` returned 200. SQL returned 4,998 SKUs;
  an AIM Act retrieval returned five hits.

Live LLM answers, a new dependency installation, Docker image construction,
and hosted deployment were not exercised. A targeted Ruff check also reported
two pre-existing style findings in `tests/test_narrative.py` (an unused `noqa`
and import ordering); this handoff does not claim a clean lint baseline.
