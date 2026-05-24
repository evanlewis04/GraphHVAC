---
entity_type: manufacturers
entity_id: Goodman
slug: goodman
template_version: 1
template_name: manufacturer.md.j2
last_built: '2026-05-24T19:54:59+00:00'
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

Goodman is a major U.S. HVAC OEM and one of the primary manufacturers tracked by this distributor [sop-tariff-response-playbook:0000:48e5f73ab0]. The brand's residential and light commercial equipment lineup spans gas furnaces, air conditioners, and heat pumps. Goodman publishes Technical Service Bulletins (TSBs) to communicate field failure patterns and voluntary replacement programs to the service channel [bulletin-goodman-tsb-2024-003-inducer-motor-bearing:0000:24f0e85c6e][bulletin-goodman-tsb-2024-012-capacitor-batch-recall:0000:1feb570a29].

## Product Categories

**Gas Furnaces** — Goodman produces a broad range of gas furnaces (GMV, GME, GMS series). Integrated furnace control (IFC) boards are a commonly stocked service part, with 2024-model fit data covering units such as the GMV104, GME68, GMS75, GMV62, GMS108, and others [spec-goodman-2024-furnace-ifc-boards:0000:a5e051befa]. List prices on IFC boards range from approximately $158 to $286 [spec-goodman-2024-furnace-ifc-boards:0000:a5e051befa].

**Air Conditioning / Heat Pumps** — Equipment models such as the GOO823 and GOO769 are represented in service and counter activity [bulletin-goodman-tsb-2024-003-inducer-motor-bearing:0000:24f0e85c6e][ticket-counter-day-2025-q1#TKT-2025-Q1-009:0000:b87f1db753].

**Components / Service Parts** — Active TSB-driven service parts include:
- Sealed-bearing inducer motor variant GO-62231, replacing open-bearing units on GOO823 [bulletin-goodman-tsb-2024-003-inducer-motor-bearing:0000:24f0e85c6e]
- 35 MFD / 440V dual-run capacitors (batch GO-67105 subject to voluntary recall) [bulletin-goodman-tsb-2024-012-capacitor-batch-recall:0000:1feb570a29]
- IFC control boards for GMV, GME, and GMS furnace families [spec-goodman-2024-furnace-ifc-boards:0000:a5e051befa]

## Regulatory Posture

**Refrigerant transition:** Goodman/Amana is primarily aligned with **R-32** for its residential lineup as of 2024-Q4, with some R-454B SKUs appearing in the commercial line [bulletin-r-32-transition-overview:0000:29e90451bd][bulletin-r-454b-overview:0000:5abf4e6fa7]. This places Goodman in the R-32 camp alongside Daikin and Mitsubishi, distinct from Carrier, Trane, and Lennox which have standardized on R-454B [bulletin-r-32-transition-overview:0000:29e90451bd]. Both R-32 and R-454B carry an ASHRAE A2L (mildly flammable) classification, requiring A2L-rated tools, leak detectors, and installer training for service work on Goodman equipment manufactured for 2025+ [bulletin-r-32-transition-overview:0000:29e90451bd].

**EPA AIM Act / Technology Transitions Rule:** New Goodman residential and light commercial equipment manufactured from January 1, 2025 onward must use refrigerants with GWP < 700, eliminating R-410A from new production [bulletin-epa-aim-act-summary:0000:2219085edc]. R-32 (GWP ~675) satisfies this threshold [bulletin-epa-aim-act-summary:0000:2219085edc].

**Warranty terms (from current TSBs):**
- Standard parts warranty: 5 years (inducer motor) [bulletin-goodman-tsb-2024-003-inducer-motor-bearing:0000:24f0e85c6e]
- Capacitor batch recall: full credit within 90 days on installed failures; standard 1-year on replacements [bulletin-goodman-tsb-2024-012-capacitor-batch-recall:0000:1feb570a29]
