---
entity_type: procedures
entity_id: tariff-response-playbook
slug: tariff-response-playbook
template_version: 1
template_name: procedure.md.j2
last_built: '2026-05-19T03:34:13+00:00'
source_chunks:
- sop-supplier-bulletin-triage:0000:9620fe3cf5
- manual-synth-install-residential-condenser:0000:dc2822e656
- email-carrier-tariff-passthrough-2025-03:0000:c1e7dd2120
- sop-price-book-update-procedure:0000:b0b51285b2
- sop-top-customer-pricing-communication:0000:8fb4cc6cc8
- email-coastal-hvac-supply-2024-06-24-price-increase-018:0000:95359591c9
- email-munch-s-supply-2024-06-28-rebate-program-019:0000:9f0c19d33a
- ticket-counter-day-2025-q1#TKT-2025-Q1-006:0000:b8b7b3c15c
- ticket-contractor-notes-2024-q4#TKT-2024-Q4-003:0000:e903bee253
- email-goodin-company-2024-08-26-product-discontinuation-023:0000:c24894e12b
- email-lennox-2025-q1-allocations:0000:848d0c2bdb
- sop-tariff-response-playbook:0000:48e5f73ab0
synthesizer: deterministic
---

# tariff-response-playbook

_This page was assembled without LLM synthesis (no `ANTHROPIC_API_KEY` or `--no-llm` was used). Content below is a structured list of supporting source chunks; set the API key and rebuild for narrative synthesis._

## Purpose

> # Supplier bulletin triage

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
- `program` — new re… [sop-supplier-bulletin-triage:0000:9620fe3cf5]

> # Residential split-system condenser — installation procedure

Generic procedure used in our counter-day training material. Not a
substitute for the OEM install manual that ships with the unit. For
specific torque, charge, and clearance values consult the manufacturer
document — e.g.
[[bulletins/mfr-carrier-tsb-2024-007-fan-motor]] for fan-motor specs,
or the model-specific install IO sheet from the OEM.

## 1. Site survey

Before pulling stock for the install:

- Confirm electrical service capacity for the new unit's MCA / MOP
  rating. Most 2.0–5.0 ton residential condensers run 25–60A on… [manual-synth-install-residential-condenser:0000:dc2822e656]

## Steps

_No source coverage._

## Citations

_No source coverage._

## Additional Source Material

> # Supplier bulletin triage

Owner: Purchasing. Last reviewed: 2023-Q3.

Every supplier email, TSB, or bulletin arrives somewhere. This is the
funnel.

## Inbox routing

Bulletins land in `purchasing@<our-domain>` from supplier rep email
distros. Purchasing assistant reviews twice daily (10am, 3pm). Each
bulletin gets tagged:

- `pricing` — any price change.
- `allocation` — supplier is constrainin… [sop-supplier-bulletin-triage:0000:9620fe3cf5]

> # Residential split-system condenser — installation procedure

Generic procedure used in our counter-day training material. Not a
substitute for the OEM install manual that ships with the unit. For
specific torque, charge, and clearance values consult the manufacturer
document — e.g.
[[bulletins/mfr-carrier-tsb-2024-007-fan-motor]] for fan-motor specs,
or the model-specific install IO sheet from t… [manual-synth-install-residential-condenser:0000:dc2822e656]

> # Carrier Enterprise — 2025-03 tariff pass-through

---

**From:** Diane Yu <dyu@carrierenterprise.example>
**To:** purchasing@graph-distributor.example
**Date:** 2025-03-02 11:08 EST
**Subject:** 2025-03 price adjustment — Section 301 pass-through

Hi all,

Heads up: effective **2025-03-17** Carrier will pass through a **4.2%
increase** across the residential condenser, heat pump, and packaged
un… [email-carrier-tariff-passthrough-2025-03:0000:c1e7dd2120]

> # Price book update procedure

Owner: Operations. Internal SOP.

## Section 1

Quarterly price book refresh is the primary cadence. Off-cycle updates triggered by supplier price changes follow the tariff playbook (see sops/tariff-response-playbook).

## Section 2

Mechanics: pull updated supplier costs into the staging table, apply category margin policy, generate the proposed price book, review w… [sop-price-book-update-procedure:0000:b0b51285b2]

> # Top customer pricing communication template

Owner: Operations. Internal SOP.

## Section 1

Triggered by any pricing change affecting a top-25 customer's commonly-purchased SKUs.

## Section 2

Channel: direct call from account rep, followed by an email confirming the conversation.

## Section 3

Content: effective date, magnitude, the substitute path if one exists, an offer for a pre-buy at th… [sop-top-customer-pricing-communication:0000:8fb4cc6cc8]

> # Coastal HVAC Supply — Q3 price adjustment — Contactor line

---

**From:** Jamie Carrillo <jamie.carrillo@coastalhvacsupply.example>
**To:** purchasing@graph-distributor.example
**Date:** 2024-06-24 10:57 EST
**Subject:** Q3 price adjustment — Contactor line

We're writing to confirm a 3% list price adjustment on the Contactor line, effective 2024-08-15. The change reflects raw material cost pre… [email-coastal-hvac-supply-2024-06-24-price-increase-018:0000:95359591c9]

> # Munch's Supply — 2025 Volume Plus rebate program — enrollment open

---

**From:** Carlos Romero <carlos.romero@munchssupply.example>
**To:** purchasing@graph-distributor.example
**Date:** 2024-06-28 10:44 EST
**Subject:** 2025 Volume Plus rebate program — enrollment open

Enrollment is now open for the 2025 Volume Plus program. Tier thresholds, accrual basis, and program-year boundaries are unc… [email-munch-s-supply-2024-06-28-rebate-program-019:0000:9f0c19d33a]

> Ticket TKT-2025-Q1-006 (2025-02-23, customer CUS-0007)
manufacturer: York | equipment_model: YOR698 | warehouse: WH-CHA

Notes: customer asked: R-410A pre-buy quote for 50 cylinders, picked up at WH-CHA [ticket-counter-day-2025-q1#TKT-2025-Q1-006:0000:b8b7b3c15c]

> Ticket TKT-2024-Q4-003 (2024-10-06, customer CUS-0496)
manufacturer: Mitsubishi | equipment_model: MIT612 | warehouse: WH-CHA

Notes: counter call — do you have 25-lb R-454B cylinders in stock at WH-CHA?. Followed up by email. [ticket-contractor-notes-2024-q4#TKT-2024-Q4-003:0000:e903bee253]

> # Goodin Company — End-of-life notice — HON390 series

---

**From:** Carlos Romero <carlos.romero@goodincompany.example>
**To:** purchasing@graph-distributor.example
**Date:** 2024-08-26 10:16 EST
**Subject:** End-of-life notice — HON390 series

The HON390 series will reach end-of-production on 2024-09-22. Terminal inventory will be allocated to active orders only; no new POs against HON390 accep… [email-goodin-company-2024-08-26-product-discontinuation-023:0000:c24894e12b]

> # Lennox 2025-Q1 allocation thread

---

**From:** Marcus Hale <mhale@lennoxpros.example>
**To:** purchasing@graph-distributor.example
**Cc:** allocation@lennoxpros.example
**Date:** 2025-01-08 09:14 EST
**Subject:** 2025-Q1 condenser allocation update — action requested

Hi team,

Quick note on the Q1 allocation for residential condenser lines. As
you know we transitioned the bulk of the resident… [email-lennox-2025-q1-allocations:0000:848d0c2bdb]

> # Tariff response playbook

How we respond when a supplier announces a tariff-driven price change
or allocation cut. Owner: VP Operations. Last reviewed: 2024-Q1.

## When this triggers

Any of:

- A supplier email announces a price increase of >5% on a category we
  carry, attributed to tariffs (Section 232 steel/aluminum, Section
  301 China, anti-dumping, etc.).
- A supplier announces an alloca… [sop-tariff-response-playbook:0000:48e5f73ab0]

