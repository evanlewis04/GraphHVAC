---
entity_type: manufacturers
entity_id: Goodman
slug: goodman
template_version: 1
template_name: manufacturer.md.j2
last_built: '2026-05-19T03:34:13+00:00'
source_chunks:
- bulletin-goodman-tsb-2024-003-inducer-motor-bearing:0000:24f0e85c6e
- sop-r-410a-retrofit-customer-outreach:0000:2349bfb54c
- sop-warranty-claim-escalation:0000:f84fc045a9
- bulletin-epa-aim-act-summary:0000:2219085edc
- bulletin-goodman-tsb-2024-012-capacitor-batch-recall:0000:1feb570a29
- spec-goodman-2024-furnace-ifc-boards:0000:a5e051befa
- sop-tariff-response-playbook:0000:48e5f73ab0
- bulletin-r-32-transition-overview:0000:29e90451bd
- bulletin-r-454b-overview:0000:5abf4e6fa7
- ticket-counter-day-2025-q1#TKT-2025-Q1-009:0000:b87f1db753
synthesizer: deterministic
---

# Goodman

_This page was assembled without LLM synthesis (no `ANTHROPIC_API_KEY` or `--no-llm` was used). Content below is a structured list of supporting source chunks; set the API key and rebuild for narrative synthesis._

## Overview

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

> # Goodman Technical Service Bulletin 2024-003

Subject: inducer motor on GOO823 — bearing wear after extended cycle counts.

Symptom: inducer motor audible bearing growl, progressing over 2-3 months, eventual lock-up. Affects units operating in dirty environments (commercial kitchens, agricultural).

Resolution: replace with sealed-bearing variant GO-62231. Customer is responsible for adding filtr… [bulletin-goodman-tsb-2024-003-inducer-motor-bearing:0000:24f0e85c6e]

> # R-410A retrofit — customer outreach playbook

Owner: Sales Ops. Last reviewed: 2024-Q1. Driving doc:
[[bulletins/r-410a-phase-out-timeline]].

## Purpose

Reach contractor customers who carry high R-410A exposure with a
proactive replacement-quote offer **before** their installed base
starts hitting service costs they can't pass on.

## Identify the target list

Run the standard exposure query:… [sop-r-410a-retrofit-customer-outreach:0000:2349bfb54c]

> # Warranty claim escalation

Owner: Customer Service. Last reviewed: 2023-Q4.

## Tier 1 — counter staff (Day 0)

Counter staff or phone-line CSR receives a warranty claim from a
contractor. Standard claim packet:

- Original invoice (date, customer, SKU, serial #).
- Failure description from the contractor.
- Photos of the failed part on installed equipment.
- Service tech name and certification… [sop-warranty-claim-escalation:0000:f84fc045a9]

> # AIM Act HFC phase-down — operational summary

This is a paraphrased operational summary of the EPA American Innovation
and Manufacturing Act (AIM Act). It is not the original regulatory text.
For the authoritative version see the EPA Final Rule (40 CFR Part 84).

## What the AIM Act does

The AIM Act phases down the U.S. production and import of
hydrofluorocarbon (HFC) refrigerants on a fixed al… [bulletin-epa-aim-act-summary:0000:2219085edc]

> # Goodman Technical Service Bulletin 2024-012

Subject: 35 MFD / 440V dual-run capacitor — voluntary replacement of batch GO-67105.

Symptom: a subset of capacitors from production batch GO-67105 were measured at 8–12% under rated capacitance out of bag. Symptom in the field is hard-start on the compressor and compressor short-cycling.

Resolution: replace any in-stock units from the affected batc… [bulletin-goodman-tsb-2024-012-capacitor-batch-recall:0000:1feb570a29]

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

> # Tariff response playbook

How we respond when a supplier announces a tariff-driven price change
or allocation cut. Owner: VP Operations. Last reviewed: 2024-Q1.

## When this triggers

Any of:

- A supplier email announces a price increase of >5% on a category we
  carry, attributed to tariffs (Section 232 steel/aluminum, Section
  301 China, anti-dumping, etc.).
- A supplier announces an alloca… [sop-tariff-response-playbook:0000:48e5f73ab0]

> Ticket TKT-2025-Q1-009 (2025-03-27, customer CUS-0041)
manufacturer: Goodman | equipment_model: GOO769 | warehouse: WH-CHA

Notes: customer asked: do you have 25-lb R-454B cylinders in stock at WH-CHA? [ticket-counter-day-2025-q1#TKT-2025-Q1-009:0000:b87f1db753]

