---
entity_type: manufacturers
entity_id: Carrier
slug: carrier
template_version: 1
template_name: manufacturer.md.j2
last_built: '2026-05-19T03:33:19+00:00'
source_chunks:
- sop-warranty-claim-escalation:0000:f84fc045a9
- ticket-contractor-notes-2024-q3#TKT-2024-Q3-006:0000:ba26e7ef0f
- ticket-warranty-claims-2024#TKT-MS-2024-004:0000:aa4f4e47af
- ticket-contractor-notes-2024-q3#TKT-2024-Q3-007:0000:8f42e66d1c
- email-carrier-tariff-passthrough-2025-03:0000:c1e7dd2120
- email-munch-s-supply-2025-02-18-delivery-delay-024:0000:157f4a6f23
- ticket-contractor-notes-2024-q3#TKT-2024-Q3-003:0000:9caf625514
- manual-synth-install-residential-condenser:0000:dc2822e656
- spec-carrier-2025-residential-condensers:0000:730402755b
- sop-supplier-bulletin-triage:0000:9620fe3cf5
synthesizer: deterministic
---

# Carrier

_This page was assembled without LLM synthesis (no `ANTHROPIC_API_KEY` or `--no-llm` was used). Content below is a structured list of supporting source chunks; set the API key and rebuild for narrative synthesis._

## Overview

> # Warranty claim escalation

Owner: Customer Service. Last reviewed: 2023-Q4.

## Tier 1 — counter staff (Day 0)

Counter staff or phone-line CSR receives a warranty claim from a
contractor. Standard claim packet:

- Original invoice (date, customer, SKU, serial #).
- Failure description from the contractor.
- Photos of the failed part on installed equipment.
- Service tech name and certification card #.

If the SKU is in the OEM's standard warranty window and the failure
mode is a known issue from a manufacturer TSB (see
[[bulletins/]]), counter staff processes the swap directly. SKU
flows ba… [sop-warranty-claim-escalation:0000:f84fc045a9]

> Ticket TKT-2024-Q3-006 (2024-08-29, customer CUS-0387)
manufacturer: Carrier | equipment_model: CAR816 | warehouse: WH-DAL

Notes: do you have 25-lb R-454B cylinders in stock at WH-DAL? [ticket-contractor-notes-2024-q3#TKT-2024-Q3-006:0000:ba26e7ef0f]

## Product Categories

_No source coverage._

## Regulatory Posture

_No source coverage._

## Additional Source Material

> # Warranty claim escalation

Owner: Customer Service. Last reviewed: 2023-Q4.

## Tier 1 — counter staff (Day 0)

Counter staff or phone-line CSR receives a warranty claim from a
contractor. Standard claim packet:

- Original invoice (date, customer, SKU, serial #).
- Failure description from the contractor.
- Photos of the failed part on installed equipment.
- Service tech name and certification… [sop-warranty-claim-escalation:0000:f84fc045a9]

> Ticket TKT-2024-Q3-006 (2024-08-29, customer CUS-0387)
manufacturer: Carrier | equipment_model: CAR816 | warehouse: WH-DAL

Notes: do you have 25-lb R-454B cylinders in stock at WH-DAL? [ticket-contractor-notes-2024-q3#TKT-2024-Q3-006:0000:ba26e7ef0f]

> Ticket TKT-MS-2024-004 (2024-10-28, customer CUS-0271)
manufacturer: Carrier | equipment_model: CAR499 | warehouse: WH-ATL | fault_code: LOCK | parts_used: CA-74551

Notes: intermittent humming at contactor pull-in. Within warranty? Bought 20 months ago. [ticket-warranty-claims-2024#TKT-MS-2024-004:0000:aa4f4e47af]

> Ticket TKT-2024-Q3-007 (2024-07-19, customer CUS-0275)
manufacturer: Carrier | equipment_model: CAR692 | warehouse: WH-CHI

Notes: any cross-ref on CA-29619 from a non-OEM supplier? [ticket-contractor-notes-2024-q3#TKT-2024-Q3-007:0000:8f42e66d1c]

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

> # Munch's Supply — Shipment delay notice — Thermostat

---

**From:** Lin Park <lin.park@munchssupply.example>
**To:** purchasing@graph-distributor.example
**Date:** 2025-02-18 10:10 EST
**Subject:** Shipment delay notice — Thermostat

We're seeing a 4-week delay on Thermostat shipments out of the Tipton facility due to a freight carrier issue. Your in-flight POs will be re-scheduled and you'll re… [email-munch-s-supply-2025-02-18-delivery-delay-024:0000:157f4a6f23]

> Ticket TKT-2024-Q3-003 (2024-07-18, customer CUS-0101)
manufacturer: Carrier | equipment_model: CAR173 | warehouse: WH-CHI

Notes: customer asked: any cross-ref on CA-64327 from a non-OEM supplier? [ticket-contractor-notes-2024-q3#TKT-2024-Q3-003:0000:9caf625514]

> # Residential split-system condenser — installation procedure

Generic procedure used in our counter-day training material. Not a
substitute for the OEM install manual that ships with the unit. For
specific torque, charge, and clearance values consult the manufacturer
document — e.g.
[[bulletins/mfr-carrier-tsb-2024-007-fan-motor]] for fan-motor specs,
or the model-specific install IO sheet from t… [manual-synth-install-residential-condenser:0000:dc2822e656]

> # Carrier 2025 Residential Condensers

_Carrier · Carrier · Condenser_


| model | tonnage | refrigerant | list_price | tier_2_price |
|---|---|---|---|---|
| CAR940 | 4.0 | R-410A | 5011.00 | 4637.00 |
| CAR996 | 4.0 | R-410A | 2289.00 | 3148.00 |
| CAR562 | 3.5 | R-454B | 3627.00 | 4830.00 |
| CAR512 | 5.0 | R-32 | 6559.00 | 4976.00 |
| CAR560 | 3.0 | R-410A | 6448.00 | 3097.00 |
| CAR570 | 2.5… [spec-carrier-2025-residential-condensers:0000:730402755b]

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

