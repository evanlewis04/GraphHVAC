---
source_id: sop-supplier-bulletin-triage
type: markdown
bucket: sops
title: "Supplier bulletin triage"
issuer: Internal Ops
doc_date: 2023-09-19
license: synthetic-internal
---

# Supplier bulletin triage

Owner: Purchasing. Last reviewed: 2023-Q3.

Every supplier email, TSB, or bulletin arrives somewhere. This is the
funnel.

## Inbox routing

Bulletins land in `purchasing@<our-domain>` from supplier rep email
distros. Purchasing assistant reviews twice daily (10am, 3pm). Each
bulletin gets tagged:

- `pricing` — any price change.
- `allocation` — supplier is constraining shipment quantity.
- `tariff` — pricing change attributed to tariffs.
- `tsb` — manufacturer technical service bulletin (product issue).
- `recall` — manufacturer safety recall.
- `program` — new rebate program or sales contest.
- `noise` — generic marketing, conferences, etc.

## Routing rules

| Tag         | Action                                                                |
| ----------- | --------------------------------------------------------------------- |
| `pricing`   | Run [[sops/tariff-response-playbook]] day-0 steps.                    |
| `allocation`| Run tariff playbook + flag VP Ops same day.                           |
| `tariff`    | Run tariff playbook.                                                  |
| `tsb`       | Forward to counter staff. File under `data/sources/bulletins/`.       |
| `recall`    | Forward to VP Ops + counter staff + email blast to affected customers.|
| `program`   | Forward to sales lead. File for quarterly rebate-accrual review.      |
| `noise`     | File and ignore.                                                      |

## Filing convention

Every retained bulletin is saved as a PDF or markdown under
`data/sources/bulletins/`. Filename pattern:

```
mfr-<manufacturer>-tsb-<year>-<seq>-<short-slug>.<md|pdf>
mfr-<manufacturer>-recall-<year>-<seq>-<short-slug>.<md|pdf>
supplier-<supplier>-<year>-<short-slug>.<md|pdf>
```

The ingestion pipeline picks up new files automatically on the next
run and re-indexes them.

## Watch-outs

- Some "TSBs" are actually marketing dressed as service info. The
  filename tag of `tsb` should be reserved for documents that describe
  a real product issue and a real corrective action. Otherwise file
  under bulletins with a less authoritative prefix.
- Allocation notices are often phrased as "your account has been
  prioritized" or "delivery cadence adjustment." Read past the
  euphemism.

## Examples

- [[bulletins/mfr-lennox-tsb-2024-001-icomfort]] — real TSB.
- [[bulletins/mfr-carrier-tsb-2024-007-fan-motor]] — real TSB.
- [[emails/lennox-2025-q1-allocations]] — allocation event routed
  through this triage.
