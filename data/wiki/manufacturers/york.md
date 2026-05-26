---
entity_type: manufacturers
entity_id: York
slug: york
template_version: 2
template_name: manufacturer.md.j2
last_built: '2026-05-26T14:05:07+00:00'
source_chunks:
- bulletin-york-tsb-2024-005-control-board-replacement:0000:c6422a1c4b
- bulletin-york-tsb-2024-002-capacitor-batch-recall:0000:90334a343c
- ticket-warranty-claims-2024#TKT-MS-2024-005:0000:f2ff669782
- bulletin-r-454b-overview:0000:5abf4e6fa7
- bulletin-r-32-transition-overview:0000:29e90451bd
- ticket-counter-day-2025-q1#TKT-2025-Q1-006:0000:b8b7b3c15c
- sop-r-410a-retrofit-customer-outreach:0000:2349bfb54c
- sop-tariff-response-playbook:0000:48e5f73ab0
synthesizer: llm
---

# York

## Overview

York is a major U.S. HVAC OEM offering residential and commercial heating, cooling, and heat-pump equipment. York equipment appears across distributor channels including furnaces (e.g., model YOR386), air-conditioning and heat-pump condensers (e.g., YOR121, YOR698), and associated components [bulletin-york-tsb-2024-005-control-board-replacement:0000:c6422a1c4b][ticket-warranty-claims-2024#TKT-MS-2024-005:0000:f2ff669782][ticket-counter-day-2025-q1#TKT-2025-Q1-006:0000:b8b7b3c15c]. York is tracked alongside other major OEMs — including [[manufacturers/carrier]], [[manufacturers/trane]], [[manufacturers/lennox]], [[manufacturers/rheem]], and [[manufacturers/goodman]] — as a tier-1 supplier whose price-list changes trigger the [[procedures/tariff-response-playbook]] when they fall outside the normal Q1/Q3 cadence [sop-tariff-response-playbook:0000:48e5f73ab0].

## Product Categories

York's known active product lines in this vault include:

- **Gas furnaces** — the YOR386 platform uses an IFC control board (P/N YO-66065); field issues include MOSFET drift causing intermittent ignition failures coded as pressure-switch faults (flash code 3) [bulletin-york-tsb-2024-005-control-board-replacement:0000:c6422a1c4b]. Standard parts warranty is 5 years [bulletin-york-tsb-2024-005-control-board-replacement:0000:c6422a1c4b].
- **Cooling/heat-pump condensers** — the YOR121 platform has been documented with refrigerant-side service events (liquid-line flare leaks, fault code E33, part YO-36921) [ticket-warranty-claims-2024#TKT-MS-2024-005:0000:f2ff669782].
- **Run capacitors** — York sources dual-run capacitors (35 MFD/440V) under its own part numbers (batch YO-27013). A voluntary replacement program was issued for a production batch measuring 8–12% under rated capacitance, causing hard-start and compressor short-cycling [bulletin-york-tsb-2024-002-capacitor-batch-recall:0000:90334a343c]. Warranty is full credit within 90 days of installation; 1-year standard on replacements [bulletin-york-tsb-2024-002-capacitor-batch-recall:0000:90334a343c].
- **Refrigerant (service refill)** — contractors servicing York equipment have active demand for [[refrigerants/r-410a]], with pre-buy requests documented as recently as Q1 2025 [ticket-counter-day-2025-q1#TKT-2025-Q1-006:0000:b8b7b3c15c].

## Regulatory Posture

York falls into the **partial-adoption** category for the low-GWP refrigerant transition driven by the [[regulations/aim-act]]. Some York lines are moving to [[refrigerants/r-454b]], while others are adopting [[refrigerants/r-32]] [bulletin-r-454b-overview:0000:5abf4e6fa7][bulletin-r-32-transition-overview:0000:29e90451bd]. This split-platform approach is unlike full-commitment peers such as [[manufacturers/carrier]] and [[manufacturers/trane]] (R-454B) or [[manufacturers/daikin]] and [[manufacturers/mitsubishi]] (R-32), and requires distributors to verify the refrigerant designation on a per-model-line basis before fulfilling service orders [bulletin-r-32-transition-overview:0000:29e90451bd].

Installed base still carries significant [[refrigerants/r-410a]] exposure — field requests for R-410A pre-buys on York equipment confirm active service demand into 2025 [ticket-counter-day-2025-q1#TKT-2025-Q1-006:0000:b8b7b3c15c]. Contractors servicing York R-410A units should be flagged during outreach per the R-410A retrofit playbook, as refill pricing pressure will increase through 2028 under the [[regulations/aim-act]] allowance schedule [sop-r-410a-retrofit-customer-outreach:0000:2349bfb54c].

Any York price-list update outside the normal Q1/Q3 cadence automatically triggers the [[procedures/tariff-response-playbook]] process [sop-tariff-response-playbook:0000:48e5f73ab0].
