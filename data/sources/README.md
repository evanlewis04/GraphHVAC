# Source corpus

Input documents for the ingestion pipeline. Every document fed to ingest
must be declared in [`manifest.yaml`](manifest.yaml).

## Layout

| Directory     | Contents                                                            |
| ------------- | ------------------------------------------------------------------- |
| `manuals/`    | Manufacturer install / service manuals (PDF, public anchors).        |
| `bulletins/`  | Regulatory bulletins — EPA, AHRI, state agencies (PDF, public).      |
| `sops/`       | Internal procedure docs (markdown, synthetic-internal).             |
| `tickets/`    | Service-ticket exports (JSONL, synthetic-internal).                 |
| `emails/`     | Supplier email threads (markdown or `.eml`, synthetic-internal).    |
| `specs/`      | Spec sheets and price-book extracts (PDF + CSV, mixed origin).      |

## License buckets

- **public-domain / redistributable** — checked into the repo.
- **reference-only** — listed in the manifest with a `fetch:` URL;
  pulled by `scripts/fetch_anchors.py` at setup time and **not** checked in.
- **synthetic-internal** — generated for this project, checked in.

When adding a real anchor doc, default to `reference-only` unless you've
confirmed it's freely redistributable. Better safe than sued.

See [`manifest.yaml`](manifest.yaml) for the entry schema.
