---
entity_type: procedures
entity_id: supplier-consolidation-post-mna
slug: supplier-consolidation-post-mna
template_version: 1
template_name: procedure.md.j2
last_built: '2026-05-19T03:33:19+00:00'
source_chunks:
- sop-supplier-consolidation-post-mna:0000:014bd6862b
- sop-supplier-rebate-tracking:0000:b6f847f568
- sop-price-book-update-procedure:0000:b0b51285b2
- sop-supplier-bulletin-triage:0000:9620fe3cf5
- email-goodin-company-2024-02-24-allocation-notice-009:0000:106b7f99f0
- email-coastal-hvac-supply-2024-06-24-price-increase-018:0000:95359591c9
- ticket-contractor-notes-2024-q4#TKT-2024-Q4-002:0000:803b78f848
- bulletin-carrier-tsb-2024-007-fan-motor:0000:e5466c5030
- spec-goodman-2024-furnace-ifc-boards:0000:a5e051befa
- ticket-warranty-claims-2024#TKT-MS-2024-008:0000:17c899e6c2
- bulletin-honeywell-tsb-2024-011-ecm-blower-firmware:0000:903113f43b
- email-munch-s-supply-2025-05-11-delivery-delay-021:0000:08dc259392
synthesizer: deterministic
---

# supplier-consolidation-post-mna

_This page was assembled without LLM synthesis (no `ANTHROPIC_API_KEY` or `--no-llm` was used). Content below is a structured list of supporting source chunks; set the API key and rebuild for narrative synthesis._

## Purpose

> # Supplier consolidation post-M&A

Owner: VP Operations. Last reviewed: 2024-Q1.

## Context

When we acquire a regional distributor, we typically inherit:

- 6–15 supplier relationships, often overlapping with our existing ones
- Different price tiers with the same supplier (their volume vs. ours)
- Different rebate program enrollments
- Different payment-term agreements
- Some "one-line" suppliers we don't want to keep

Goal of this SOP: reach one consolidated supplier list within 90 days
of close, with our combined volume on the best price tier we qualify for.

## Day 0–14 — inventory the i… [sop-supplier-consolidation-post-mna:0000:014bd6862b]

> # Supplier rebate tracking

Owner: Operations. Internal SOP.

## Section 1

Each supplier rebate program enrolled is recorded with: tier thresholds, accrual basis, payment cadence, program start and end dates, and our YTD volume against tier.

## Section 2

Monthly: AR-side rebate accrual is recorded as a contra-COGS entry per program.

## Section 3

Quarterly: reconcile booked accrual against the supplier's published statement. Disputes flagged to the supplier within 30 days; otherwise considered accepted.

## Section 4

Year-end: confirm program tier achievement and book any retroactive adju… [sop-supplier-rebate-tracking:0000:b6f847f568]

## Steps

_No source coverage._

## Citations

_No source coverage._

## Additional Source Material

> # Supplier consolidation post-M&A

Owner: VP Operations. Last reviewed: 2024-Q1.

## Context

When we acquire a regional distributor, we typically inherit:

- 6–15 supplier relationships, often overlapping with our existing ones
- Different price tiers with the same supplier (their volume vs. ours)
- Different rebate program enrollments
- Different payment-term agreements
- Some "one-line" supplie… [sop-supplier-consolidation-post-mna:0000:014bd6862b]

> # Supplier rebate tracking

Owner: Operations. Internal SOP.

## Section 1

Each supplier rebate program enrolled is recorded with: tier thresholds, accrual basis, payment cadence, program start and end dates, and our YTD volume against tier.

## Section 2

Monthly: AR-side rebate accrual is recorded as a contra-COGS entry per program.

## Section 3

Quarterly: reconcile booked accrual against the… [sop-supplier-rebate-tracking:0000:b6f847f568]

> # Price book update procedure

Owner: Operations. Internal SOP.

## Section 1

Quarterly price book refresh is the primary cadence. Off-cycle updates triggered by supplier price changes follow the tariff playbook (see sops/tariff-response-playbook).

## Section 2

Mechanics: pull updated supplier costs into the staging table, apply category margin policy, generate the proposed price book, review w… [sop-price-book-update-procedure:0000:b0b51285b2]

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

> # Goodin Company — Q3 allocation update — Thermostat

---

**From:** Greg Ostrowski <greg.ostrowski@goodincompany.example>
**To:** purchasing@graph-distributor.example
**Date:** 2024-02-24 10:59 EST
**Subject:** Q3 allocation update — Thermostat

Our Thermostat capacity for Q3 is allocated at 2% of trailing-quarter volume across the channel. Your account allocation specifically: see attached. We e… [email-goodin-company-2024-02-24-allocation-notice-009:0000:106b7f99f0]

> # Coastal HVAC Supply — Q3 price adjustment — Contactor line

---

**From:** Jamie Carrillo <jamie.carrillo@coastalhvacsupply.example>
**To:** purchasing@graph-distributor.example
**Date:** 2024-06-24 10:57 EST
**Subject:** Q3 price adjustment — Contactor line

We're writing to confirm a 3% list price adjustment on the Contactor line, effective 2024-08-15. The change reflects raw material cost pre… [email-coastal-hvac-supply-2024-06-24-price-increase-018:0000:95359591c9]

> Ticket TKT-2024-Q4-002 (2024-11-30, customer CUS-0336)
manufacturer: Daikin | equipment_model: DAI585 | warehouse: WH-ATL

Notes: customer asked: is DA-57598 compatible with DAI585? [ticket-contractor-notes-2024-q4#TKT-2024-Q4-002:0000:803b78f848]

> # Carrier Technical Service Bulletin 2024-007

**Subject:** 24ABC6 series condenser — replacement procedure for
condenser fan motor (HC39GE237).

**Affected models:** 24ABC6 series, all tonnages. Production dates 2021
through current.

**Severity:** Service. No safety issue. Common service repair.

## Symptom

Condenser fan motor (Carrier P/N HC39GE237, replaces obsolete
HC39GE234) reaches end of… [bulletin-carrier-tsb-2024-007-fan-motor:0000:e5466c5030]

> # Goodman 2024 Furnace Ifc Boards

_Goodman · Goodman · ControlBoard_


| part_no | model_fit | list_price | tier_2_price |
|---|---|---|---|
| GD-59578 | GMV104 | 250.00 | 215.00 |
| GD-30359 | GMV82 | 199.00 | 135.00 |
| GD-32400 | GME68 | 217.00 | 211.00 |
| GD-47127 | GME78 | 158.00 | 186.00 |
| GD-40574 | GMS75 | 173.00 | 156.00 |
| GD-65933 | GMS108 | 275.00 | 224.00 |
| GD-94387 | GMV62 | 1… [spec-goodman-2024-furnace-ifc-boards:0000:a5e051befa]

> Ticket TKT-MS-2024-008 (2024-09-21, customer CUS-0420)
manufacturer: Honeywell | equipment_model: HON772 | warehouse: WH-PHX | fault_code: P-LOW | parts_used: HO-41020

Notes: Tech: intermittent humming at contactor pull-in. Confirmed in field. Need warranty swap of HO-41020. [ticket-warranty-claims-2024#TKT-MS-2024-008:0000:17c899e6c2]

> # Honeywell Technical Service Bulletin 2024-011

Subject: ECM blower module on HON255 platform — firmware update for low-airflow alarm.

Symptom: ECM blower posts low-airflow alarm code 21 on standard 0.5 in. WC static. Customers report unit running but reduced airflow at the registers.

Resolution: Apply firmware update HO-85004 via the OEM service tool (kit ST-FW-200). Update preserves dip-switc… [bulletin-honeywell-tsb-2024-011-ecm-blower-firmware:0000:903113f43b]

> # Munch's Supply — Shipment delay notice — Motor

---

**From:** Marcus Hale <marcus.hale@munchssupply.example>
**To:** purchasing@graph-distributor.example
**Date:** 2025-05-11 10:33 EST
**Subject:** Shipment delay notice — Motor

We're seeing a 3-week delay on Motor shipments out of the Mexicali facility due to a freight carrier issue. Your in-flight POs will be re-scheduled and you'll receive a… [email-munch-s-supply-2025-05-11-delivery-delay-021:0000:08dc259392]

