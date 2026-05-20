---
entity_type: manufacturers
entity_id: Trane
slug: trane
template_version: 1
template_name: manufacturer.md.j2
last_built: '2026-05-19T03:34:13+00:00'
source_chunks:
- sop-r-410a-retrofit-customer-outreach:0000:2349bfb54c
- ticket-contractor-notes-2024-q3#TKT-2024-Q3-010:0000:693f5461f3
- bulletin-trane-tsb-2024-002-r-32-launch:0000:d16e4c2761
- email-trane-supply-2024-02-15-allocation-notice-003:0000:51a77785d6
- bulletin-r-32-transition-overview:0000:29e90451bd
- email-trane-supply-2024-07-02-product-discontinuation-008:0000:fa3faaecba
- sop-tariff-response-playbook:0000:48e5f73ab0
- bulletin-epa-aim-act-summary:0000:2219085edc
- bulletin-r-454b-overview:0000:5abf4e6fa7
- ticket-warranty-claims-2024#TKT-MS-2024-007:0000:f3482ff171
synthesizer: deterministic
---

# Trane

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

> # R-410A retrofit — customer outreach playbook

Owner: Sales Ops. Last reviewed: 2024-Q1. Driving doc:
[[bulletins/r-410a-phase-out-timeline]].

## Purpose

Reach contractor customers who carry high R-410A exposure with a
proactive replacement-quote offer **before** their installed base
starts hitting service costs they can't pass on.

## Identify the target list

Run the standard exposure query:… [sop-r-410a-retrofit-customer-outreach:0000:2349bfb54c]

> Ticket TKT-2024-Q3-010 (2024-08-26, customer CUS-0482)
manufacturer: Trane | equipment_model: TRA414 | warehouse: WH-CHA

Notes: customer asked: any cross-ref on TR-31776 from a non-OEM supplier? [ticket-contractor-notes-2024-q3#TKT-2024-Q3-010:0000:693f5461f3]

> # Trane Technical Service Bulletin 2024-002

**Subject:** 4TWR8 series heat pump — R-454B model launch. Distributor
stocking, service tool, and crossover guidance.

**Effective:** Production starts 2024-Q3 for 2025 model year.

## What's new

The 4TWR8 platform is the first Trane residential heat-pump line built
on R-454B. The 4TWR7 series (R-410A) continues in production through
end-of-life inven… [bulletin-trane-tsb-2024-002-r-32-launch:0000:d16e4c2761]

> # Trane Supply — Q3 allocation update — Thermostat

---

**From:** Carlos Romero <carlos.romero@tranesupply.example>
**To:** purchasing@graph-distributor.example
**Date:** 2024-02-15 10:48 EST
**Subject:** Q3 allocation update — Thermostat

Our Thermostat capacity for Q3 is allocated at 4% of trailing-quarter volume across the channel. Your account allocation specifically: see attached. We expect… [email-trane-supply-2024-02-15-allocation-notice-003:0000:51a77785d6]

> # Trane Supply — End-of-life notice — RHE283 series

---

**From:** Jamie Carrillo <jamie.carrillo@tranesupply.example>
**To:** purchasing@graph-distributor.example
**Date:** 2024-07-02 10:45 EST
**Subject:** End-of-life notice — RHE283 series

The RHE283 series will reach end-of-production on 2024-08-23. Terminal inventory will be allocated to active orders only; no new POs against RHE283 accepte… [email-trane-supply-2024-07-02-product-discontinuation-008:0000:fa3faaecba]

> # Tariff response playbook

How we respond when a supplier announces a tariff-driven price change
or allocation cut. Owner: VP Operations. Last reviewed: 2024-Q1.

## When this triggers

Any of:

- A supplier email announces a price increase of >5% on a category we
  carry, attributed to tariffs (Section 232 steel/aluminum, Section
  301 China, anti-dumping, etc.).
- A supplier announces an alloca… [sop-tariff-response-playbook:0000:48e5f73ab0]

> # AIM Act HFC phase-down — operational summary

This is a paraphrased operational summary of the EPA American Innovation
and Manufacturing Act (AIM Act). It is not the original regulatory text.
For the authoritative version see the EPA Final Rule (40 CFR Part 84).

## What the AIM Act does

The AIM Act phases down the U.S. production and import of
hydrofluorocarbon (HFC) refrigerants on a fixed al… [bulletin-epa-aim-act-summary:0000:2219085edc]

> Ticket TKT-MS-2024-007 (2024-10-19, customer CUS-0065)
manufacturer: Trane | equipment_model: TRA462 | warehouse: WH-ATL | fault_code: E21 | parts_used: TR-84800

Notes: Contractor reports blower not starting, ECM module fault code 21. Photos attached. Cert # 608-9271. [ticket-warranty-claims-2024#TKT-MS-2024-007:0000:f3482ff171]

