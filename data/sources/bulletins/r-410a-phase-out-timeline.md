---
source_id: bulletin-r-410a-phase-out-timeline
type: markdown
bucket: bulletins
title: "R-410A phase-out timeline and distributor impact"
issuer: Internal Compliance
refrigerants: [R-410A, R-32, R-454B]
regulations: [AIM-Act]
doc_date: 2024-02-12
license: synthetic-internal
---

# R-410A phase-out — operational timeline

Synthesized from the AIM Act Technology Transitions Rule, AHRI updates,
and OEM transition guides. For regulatory authority see
[[bulletins/epa-aim-act-summary]].

## Timeline

**Through 2024-12-31**
- R-410A residential and light-commercial AC/HP equipment may be
  manufactured and imported.
- Distributor inventory builds for the 2025 transition.

**2025-01-01**
- New manufacture and import of R-410A residential AC and HP equipment
  prohibited (Technology Transitions Rule, GWP < 700 cutoff).
- R-410A inventory already in distributor possession at 2024-12-31 may
  continue to be sold and installed.
- New OEM model years ship in R-32 or R-454B.

**2025-01-01 through 2026-12-31**
- R-410A bulk-refrigerant prices expected to climb 20–60% as AIM Act
  allowances compress (60% of baseline through 2028).
- Service refills remain legal; cost pass-through becomes a customer
  communication issue.
- Residential VRF transition window (GWP < 700) phases in through 2026.

**2027 onward**
- Allowance pressure intensifies (30% baseline starting 2029).
- Expect reclaimed-refrigerant programs to play a larger share of
  service supply.

## Distributor-side actions

1. **Inventory triage by 2024-Q4:** identify R-410A SKUs to draw down vs
   stockpile. See [[sops/inventory-reorder-policy]].
2. **Customer outreach** to contractors with R-410A-heavy job mix; see
   [[sops/r-410a-retrofit-customer-outreach]].
3. **Tagging in ERP:** every SKU's refrigerant should be tagged so
   exposure queries are one-step. (Done in our DuckDB staging table —
   `skus.refrigerant` column.)
4. **Supplier coordination:** confirm 2025 product-line mix for each
   master supplier. See [[emails/lennox-2025-q1-allocations]] and
   [[emails/carrier-tariff-passthrough-2025-03]].

## Customer messaging

We do **not** recommend telling customers "R-410A is illegal in 2025."
That is incorrect — service refills remain legal indefinitely. The
correct framing:

> R-410A residential equipment can no longer be manufactured starting
> 2025-01-01. Existing equipment can still be serviced. New
> installations after that date will use R-32 or R-454B. Pricing on
> R-410A refills will rise through the phase-down — recommend
> replacement quotes for any unit older than ~10 years.
