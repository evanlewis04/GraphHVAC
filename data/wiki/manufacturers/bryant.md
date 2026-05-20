---
entity_type: manufacturers
entity_id: Bryant
slug: bryant
template_version: 1
template_name: manufacturer.md.j2
last_built: '2026-05-19T03:33:19+00:00'
source_chunks:
- bulletin-bryant-tsb-2024-008-inducer-motor-bearing:0000:87189af649
- bulletin-r-454b-overview:0000:5abf4e6fa7
- ticket-warranty-claims-2024#TKT-MS-2024-009:0000:d6801a3406
- ticket-warranty-claims-2024#TKT-MS-2024-001:0000:1b9cb72b8e
- sop-r-410a-retrofit-customer-outreach:0000:2349bfb54c
- ticket-contractor-notes-2024-q3#TKT-2024-Q3-002:0000:9c86e28d3f
synthesizer: deterministic
---

# Bryant

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

## Product Categories

_No source coverage._

## Regulatory Posture

_No source coverage._

## Additional Source Material

> # Bryant Technical Service Bulletin 2024-008

Subject: inducer motor on BRY743 — bearing wear after extended cycle counts.

Symptom: inducer motor audible bearing growl, progressing over 2-3 months, eventual lock-up. Affects units operating in dirty environments (commercial kitchens, agricultural).

Resolution: replace with sealed-bearing variant BR-91412. Customer is responsible for adding filtra… [bulletin-bryant-tsb-2024-008-inducer-motor-bearing:0000:87189af649]

> Ticket TKT-MS-2024-009 (2024-06-10, customer CUS-0261)
manufacturer: Bryant | equipment_model: BRY832 | warehouse: WH-CHI | fault_code: P-LOW | parts_used: BR-37693

Notes: Tech: no heat, ignitor flashing 3x — likely IFC board. Confirmed in field. Need warranty swap of BR-37693. [ticket-warranty-claims-2024#TKT-MS-2024-009:0000:d6801a3406]

> Ticket TKT-MS-2024-001 (2024-02-11, customer CUS-0177)
manufacturer: Bryant | equipment_model: BRY228 | warehouse: WH-CHA | fault_code: LOCK | parts_used: BR-21017

Notes: condenser fan locked rotor — bearing growl history. Within warranty? Bought 5 months ago. [ticket-warranty-claims-2024#TKT-MS-2024-001:0000:1b9cb72b8e]

> # R-410A retrofit — customer outreach playbook

Owner: Sales Ops. Last reviewed: 2024-Q1. Driving doc:
[[bulletins/r-410a-phase-out-timeline]].

## Purpose

Reach contractor customers who carry high R-410A exposure with a
proactive replacement-quote offer **before** their installed base
starts hitting service costs they can't pass on.

## Identify the target list

Run the standard exposure query:… [sop-r-410a-retrofit-customer-outreach:0000:2349bfb54c]

> Ticket TKT-2024-Q3-002 (2024-09-09, customer CUS-0048)
manufacturer: Bryant | equipment_model: BRY308 | warehouse: WH-PHX

Notes: customer asked: training kit for A2L service — what's in it? [ticket-contractor-notes-2024-q3#TKT-2024-Q3-002:0000:9c86e28d3f]

