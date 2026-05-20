---
entity_type: manufacturers
entity_id: York
slug: york
template_version: 1
template_name: manufacturer.md.j2
last_built: '2026-05-19T03:34:13+00:00'
source_chunks:
- bulletin-york-tsb-2024-005-control-board-replacement:0000:c6422a1c4b
- bulletin-york-tsb-2024-002-capacitor-batch-recall:0000:90334a343c
- sop-r-410a-retrofit-customer-outreach:0000:2349bfb54c
- ticket-counter-day-2025-q1#TKT-2025-Q1-006:0000:b8b7b3c15c
- sop-tariff-response-playbook:0000:48e5f73ab0
- ticket-warranty-claims-2024#TKT-MS-2024-005:0000:f2ff669782
- bulletin-r-454b-overview:0000:5abf4e6fa7
- bulletin-r-32-transition-overview:0000:29e90451bd
synthesizer: deterministic
---

# York

_This page was assembled without LLM synthesis (no `ANTHROPIC_API_KEY` or `--no-llm` was used). Content below is a structured list of supporting source chunks; set the API key and rebuild for narrative synthesis._

## Overview

> # R-454B — replacement refrigerant overview

R-454B (trade name Opteon XL41, Solstice 454B) is the leading low-GWP
replacement chosen by Carrier, Trane, and Lennox for U.S. residential
AC and heat-pump equipment in 2025+ model years.

## Properties

| Property                 | R-454B          | R-410A     |
| ------------------------ | --------------- | ---------- |
| ASHRAE classification    | A2L (mildly flammable) | A1 (non-flammable) |
| GWP (AR4)                | 466             | 2088       |
| Composition              | 68.9% R-32 / 31.1% R-1234yf | 50/50 R-32/R-125 |
| Glide… [bulletin-r-454b-overview:0000:5abf4e6fa7]

> # R-32 — replacement refrigerant overview

R-32 (difluoromethane) is one of two leading low-GWP replacements for
R-410A in U.S. residential AC and heat-pump equipment. The other is
R-454B; see [[bulletins/r-454b-overview]].

## Properties

| Property                 | R-32          | R-410A     |
| ------------------------ | ------------- | ---------- |
| ASHRAE classification    | A2L (mildly flammable) | A1 (non-flammable) |
| GWP (AR4)                | 675           | 2088       |
| Single-component         | Yes           | No (blend) |
| Glide                    | None          | Low… [bulletin-r-32-transition-overview:0000:29e90451bd]

## Product Categories

_No source coverage._

## Regulatory Posture

_No source coverage._

## Additional Source Material

> # York Technical Service Bulletin 2024-005

Subject: YOR386 furnace IFC control board (P/N YO-66065) replacement procedure.

Symptom: intermittent ignition failure; status LED shows flash code 3 (pressure switch). Confirmed not to be a pressure switch failure — control board MOSFET drift on extended cycles.

Resolution: replace IFC board with YO-66065. Procedure: shut off gas, kill power, label al… [bulletin-york-tsb-2024-005-control-board-replacement:0000:c6422a1c4b]

> # York Technical Service Bulletin 2024-002

Subject: 35 MFD / 440V dual-run capacitor — voluntary replacement of batch YO-27013.

Symptom: a subset of capacitors from production batch YO-27013 were measured at 8–12% under rated capacitance out of bag. Symptom in the field is hard-start on the compressor and compressor short-cycling.

Resolution: replace any in-stock units from the affected batch.… [bulletin-york-tsb-2024-002-capacitor-batch-recall:0000:90334a343c]

> # R-410A retrofit — customer outreach playbook

Owner: Sales Ops. Last reviewed: 2024-Q1. Driving doc:
[[bulletins/r-410a-phase-out-timeline]].

## Purpose

Reach contractor customers who carry high R-410A exposure with a
proactive replacement-quote offer **before** their installed base
starts hitting service costs they can't pass on.

## Identify the target list

Run the standard exposure query:… [sop-r-410a-retrofit-customer-outreach:0000:2349bfb54c]

> Ticket TKT-2025-Q1-006 (2025-02-23, customer CUS-0007)
manufacturer: York | equipment_model: YOR698 | warehouse: WH-CHA

Notes: customer asked: R-410A pre-buy quote for 50 cylinders, picked up at WH-CHA [ticket-counter-day-2025-q1#TKT-2025-Q1-006:0000:b8b7b3c15c]

> # Tariff response playbook

How we respond when a supplier announces a tariff-driven price change
or allocation cut. Owner: VP Operations. Last reviewed: 2024-Q1.

## When this triggers

Any of:

- A supplier email announces a price increase of >5% on a category we
  carry, attributed to tariffs (Section 232 steel/aluminum, Section
  301 China, anti-dumping, etc.).
- A supplier announces an alloca… [sop-tariff-response-playbook:0000:48e5f73ab0]

> Ticket TKT-MS-2024-005 (2024-10-25, customer CUS-0462)
manufacturer: York | equipment_model: YOR121 | warehouse: WH-CHA | fault_code: E33 | parts_used: YO-36921

Notes: Contractor reports low refrigerant — leak at flare on liquid line. Photos attached. Cert # 608-4417. [ticket-warranty-claims-2024#TKT-MS-2024-005:0000:f2ff669782]

