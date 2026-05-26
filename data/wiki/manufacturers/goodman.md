---
entity_type: manufacturers
entity_id: Goodman
slug: goodman
template_version: 2
template_name: manufacturer.md.j2
last_built: '2026-05-26T14:06:22+00:00'
source_chunks:
- bulletin-goodman-tsb-2024-003-inducer-motor-bearing:0000:24f0e85c6e
- ticket-counter-day-2025-q1#TKT-2025-Q1-009:0000:b87f1db753
- bulletin-goodman-tsb-2024-012-capacitor-batch-recall:0000:1feb570a29
- bulletin-r-454b-overview:0000:5abf4e6fa7
- bulletin-r-32-transition-overview:0000:29e90451bd
- sop-r-410a-retrofit-customer-outreach:0000:2349bfb54c
- bulletin-epa-aim-act-summary:0000:2219085edc
- spec-goodman-2024-furnace-ifc-boards:0000:a5e051befa
- sop-warranty-claim-escalation:0000:f84fc045a9
- sop-tariff-response-playbook:0000:48e5f73ab0
synthesizer: llm
---

# Goodman

## Overview

Goodman is a major U.S. residential and light-commercial HVAC equipment manufacturer, commonly stocked alongside [[manufacturers/amana]] (a sibling brand under the same parent structure). Goodman is owned by [[manufacturers/daikin]], which also influences its refrigerant transition strategy [bulletin-r-32-transition-overview:0000:29e90451bd]. The brand appears regularly in distributor order flows and tariff-monitoring watchlists alongside [[manufacturers/carrier]], [[manufacturers/trane]], [[manufacturers/lennox]], [[manufacturers/rheem]], and [[manufacturers/york]] as a top-tier OEM whose price-list changes outside normal Q1/Q3 cadence trigger the [[procedures/tariff-response-playbook]] [sop-tariff-response-playbook:0000:48e5f73ab0].

Goodman equipment covered in this vault spans gas furnaces, air conditioners, and heat pumps. Active technical service bulletins (TSBs) in 2024 address inducer motor bearing failures and a capacitor batch recall, indicating a mid-volume service parts demand profile at the counter [bulletin-goodman-tsb-2024-003-inducer-motor-bearing:0000:24f0e85c6e][bulletin-goodman-tsb-2024-012-capacitor-batch-recall:0000:1feb570a29].

---

## Product Categories

**Gas Furnaces** — Goodman's 2024 furnace lineup covers GMV, GME, and GMS model series. IFC (integrated furnace control) boards are stocked across 25+ model-fit SKUs, with list prices ranging from approximately $158 to $286 and tier-2 pricing varying by model [spec-goodman-2024-furnace-ifc-boards:0000:a5e051befa].

**Air Conditioners / Heat Pumps** — Field tickets reference equipment models such as GOO769 and GOO823, indicating active installed base in the field requiring refrigerant and component support [ticket-counter-day-2025-q1#TKT-2025-Q1-009:0000:b87f1db753][bulletin-goodman-tsb-2024-003-inducer-motor-bearing:0000:24f0e85c6e].

**Service Parts** — Two notable 2024 service actions:

- **Inducer motor (GO-62231):** Sealed-bearing replacement for bearing wear on model GOO823, covered under standard 5-year parts warranty. Environmental filtration is contractor responsibility [bulletin-goodman-tsb-2024-003-inducer-motor-bearing:0000:24f0e85c6e].
- **Dual-run capacitor (batch GO-67105):** Voluntary replacement program for 35 MFD / 440V units measuring 8–12% under rated capacitance, causing compressor hard-start and short-cycling. Full credit within 90 days; standard 1-year warranty on replacements [bulletin-goodman-tsb-2024-012-capacitor-batch-recall:0000:1feb570a29].

---

## Regulatory Posture

Goodman's refrigerant transition path diverges from [[manufacturers/carrier]], [[manufacturers/trane]], and [[manufacturers/lennox]], which have standardized on [[refrigerants/r-454b]]. Goodman/[[manufacturers/amana]] is primarily adopting [[refrigerants/r-32]] for residential lines, with some [[refrigerants/r-454b]] SKUs appearing in the commercial lineup [bulletin-r-32-transition-overview:0000:29e90451bd][bulletin-r-454b-overview:0000:5abf4e6fa7]. This aligns with parent [[manufacturers/daikin]]'s long-standing global commitment to R-32 [bulletin-r-32-transition-overview:0000:29e90451bd].

Both paths satisfy the [[regulations/aim-act]] Technology Transitions Rule mandate restricting new residential and light-commercial equipment to refrigerants with GWP < 700 starting January 1, 2025 — [[refrigerants/r-410a]] (GWP ~2088) does not qualify, while R-32 (GWP ~675) and [[refrigerants/r-454b]] (GWP ~466) both clear the threshold [bulletin-epa-aim-act-summary:0000:2219085edc].

Distributor implication: counter staff must verify per-model refrigerant type on Goodman equipment orders. R-32 and [[refrigerants/r-410a]] **cannot** be mixed in the same system; bulk inventory must be strictly segregated [bulletin-r-32-transition-overview:0000:29e90451bd]. Field inquiries for [[refrigerants/r-454b]] cylinders have also been logged against Goodman commercial equipment (model GOO769), so dual-refrigerant stocking is required [ticket-counter-day-2025-q1#TKT-2025-Q1-009:0000:b87f1db753].
