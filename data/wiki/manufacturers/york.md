---
entity_type: manufacturers
entity_id: York
slug: york
template_version: 1
template_name: manufacturer.md.j2
last_built: '2026-05-24T19:51:29+00:00'
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

York is a major HVAC original equipment manufacturer (OEM) tracked as a primary supplier in distributor operations. York equipment appears across residential and light-commercial segments, with active warranty claims, technical service bulletins, and field service activity on record. York is listed alongside Carrier, Trane, Lennox, Goodman, Rheem, and Daikin as a major OEM whose price-list changes trigger distributor-level tariff response protocols. [sop-tariff-response-playbook:0000:48e5f73ab0]

## Product Categories

York's documented product lines include:

- **Gas furnaces** — specifically the YOR386 model, which uses the IFC control board (P/N YO-66065). A known failure mode involves MOSFET drift causing intermittent ignition failure (flash code 3) on extended cycles. [bulletin-york-tsb-2024-005-control-board-replacement:0000:c6422a1c4b]
- **Residential AC / heat pump systems** — including the YOR121 and YOR698 models. Field tickets show refrigerant-side service activity (leak at flare on liquid line, fault code E33) on YOR121 units. [ticket-warranty-claims-2024#TKT-MS-2024-005:0000:f2ff669782] YOR698 customers have been quoted R-410A cylinder pre-buys for the 2025 service season. [ticket-counter-day-2025-q1#TKT-2025-Q1-006:0000:b8b7b3c15c]
- **Run capacitors** — York sources 35 MFD / 440V dual-run capacitors (P/N YO-27013). A voluntary replacement program was issued for a production batch found 8–12% under rated capacitance, causing hard-starts and compressor short-cycling. [bulletin-york-tsb-2024-002-capacitor-batch-recall:0000:90334a343c]

## Regulatory Posture

York has taken a split approach to the R-410A phase-out transition. York is identified as a **partial R-454B adopter** on some lines [bulletin-r-454b-overview:0000:5abf4e6fa7], while other sources list York in the **R-454B adopter** column for residential models. [bulletin-r-32-transition-overview:0000:29e90451bd] York does not appear to be a primary R-32 platform (that position belongs to Daikin, Mitsubishi, and parts of Goodman/Amana). [bulletin-r-32-transition-overview:0000:29e90451bd]

Key servicing implications for York equipment during the refrigerant transition:
- Verify on a per-model basis whether the unit requires R-454B or R-32, as York uses both. [bulletin-r-454b-overview:0000:5abf4e6fa7][bulletin-r-32-transition-overview:0000:29e90451bd]
- A2L-rated tools, leak detectors, and technician training are required for both replacement refrigerants. [bulletin-r-454b-overview:0000:5abf4e6fa7]
- Warranty on York parts varies by component: 5-year on IFC control boards [bulletin-york-tsb-2024-005-control-board-replacement:0000:c6422a1c4b]; 1-year standard / 90-day full credit on the recalled capacitor batch. [bulletin-york-tsb-2024-002-capacitor-batch-recall:0000:90334a343c]
