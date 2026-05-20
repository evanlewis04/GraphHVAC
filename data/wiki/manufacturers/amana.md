---
entity_type: manufacturers
entity_id: Amana
slug: amana
template_version: 1
template_name: manufacturer.md.j2
last_built: '2026-05-19T03:33:19+00:00'
source_chunks:
- ticket-contractor-notes-2024-q4#TKT-2024-Q4-001:0000:6a30587082
- ticket-warranty-claims-2024#TKT-MS-2024-006:0000:6f66251535
- ticket-contractor-notes-2024-q3#TKT-2024-Q3-004:0000:30abce54f6
- bulletin-amana-tsb-2024-010-control-board-replacement:0000:d19a6155e1
- sop-r-410a-retrofit-customer-outreach:0000:2349bfb54c
- ticket-contractor-notes-2024-q4#TKT-2024-Q4-010:0000:0fd2f74a2a
- ticket-counter-day-2025-q1#TKT-2025-Q1-005:0000:12bf609454
- ticket-contractor-notes-2024-q3#TKT-2024-Q3-009:0000:d26e149143
- bulletin-r-454b-overview:0000:5abf4e6fa7
- bulletin-r-32-transition-overview:0000:29e90451bd
synthesizer: deterministic
---

# Amana

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

> Ticket TKT-2024-Q4-001 (2024-11-29, customer CUS-0243)
manufacturer: Amana | equipment_model: AMA352 | warehouse: WH-DAL

Notes: need substitute for AM-66203 — backordered 6 weeks [ticket-contractor-notes-2024-q4#TKT-2024-Q4-001:0000:6a30587082]

> Ticket TKT-MS-2024-006 (2024-08-09, customer CUS-0098)
manufacturer: Amana | equipment_model: AMA568 | warehouse: WH-PHX | fault_code: P-LOW | parts_used: AM-65174

Notes: Tech: evap freezing up — low airflow, restricted filter. Confirmed in field. Need warranty swap of AM-65174. [ticket-warranty-claims-2024#TKT-MS-2024-006:0000:6f66251535]

> Ticket TKT-2024-Q3-004 (2024-08-10, customer CUS-0235)
manufacturer: Amana | equipment_model: AMA180 | warehouse: WH-ATL

Notes: customer asked: is AM-11532 compatible with AMA180? [ticket-contractor-notes-2024-q3#TKT-2024-Q3-004:0000:30abce54f6]

> # Amana Technical Service Bulletin 2024-010

Subject: AMA460 furnace IFC control board (P/N AM-62867) replacement procedure.

Symptom: intermittent ignition failure; status LED shows flash code 3 (pressure switch). Confirmed not to be a pressure switch failure — control board MOSFET drift on extended cycles.

Resolution: replace IFC board with AM-62867. Procedure: shut off gas, kill power, label a… [bulletin-amana-tsb-2024-010-control-board-replacement:0000:d19a6155e1]

> # R-410A retrofit — customer outreach playbook

Owner: Sales Ops. Last reviewed: 2024-Q1. Driving doc:
[[bulletins/r-410a-phase-out-timeline]].

## Purpose

Reach contractor customers who carry high R-410A exposure with a
proactive replacement-quote offer **before** their installed base
starts hitting service costs they can't pass on.

## Identify the target list

Run the standard exposure query:… [sop-r-410a-retrofit-customer-outreach:0000:2349bfb54c]

> Ticket TKT-2024-Q4-010 (2024-10-24, customer CUS-0376)
manufacturer: Amana | equipment_model: AMA415 | warehouse: WH-DAL

Notes: counter call — need substitute for AM-48474 — backordered 6 weeks. Followed up by email. [ticket-contractor-notes-2024-q4#TKT-2024-Q4-010:0000:0fd2f74a2a]

> Ticket TKT-2025-Q1-005 (2025-01-13, customer CUS-0395)
manufacturer: Amana | equipment_model: AMA532 | warehouse: WH-PHX

Notes: counter call — training kit for A2L service — what's in it?. Followed up by email. [ticket-counter-day-2025-q1#TKT-2025-Q1-005:0000:12bf609454]

> Ticket TKT-2024-Q3-009 (2024-07-04, customer CUS-0186)
manufacturer: Amana | equipment_model: AMA184 | warehouse: WH-DAL

Notes: counter call — training kit for A2L service — what's in it?. Followed up by email. [ticket-contractor-notes-2024-q3#TKT-2024-Q3-009:0000:d26e149143]

