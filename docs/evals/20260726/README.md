# Historical evaluation archive: 2026-07-26

These 18 JSON/JSONL files were previously untracked in the original checkout's
`data/evals/` directory. They are preserved byte-for-byte for continuation on
another machine, outside the live Admin Evals directory so partial comparison
runs do not become the application's current headline metrics.

- `151456-retrieval`: six questions, with summary.
- `151550-retrieval`: 30 questions, with summary.
- `151510-agent`: seven recorded Haiku answers, no completed summary.
- `5qid-sonnet46` and `5qid-sonnet5`: five-question comparisons, with summaries.
- `q12-sonnet46` and `q12-sonnet5`: single-question comparisons, with summaries.
- `haiku-4qid`: four-question comparison, with summary.
- The three `6qid-combined` JSONL files combine question subsets; they have no
  corresponding summary files here.

Use the `model` field in each agent row, not filenames alone, to identify the
recorded model. Token costs and answers are historical outputs, not newly
verified prices or correctness claims. Trace IDs refer to the original local
audit database, which is not checked in. See `tests/eval/baseline.summary.json`
for the separately pinned baseline and `scripts/run_evals.py` to run new evals.
