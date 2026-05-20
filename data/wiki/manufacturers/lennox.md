---
entity_type: manufacturers
entity_id: Lennox
slug: lennox
template_version: 1
template_name: manufacturer.md.j2
last_built: '2026-05-19T03:34:07+00:00'
source_chunks:
- bulletin-lennox-tsb-2024-001-icomfort:0000:854994a674
- ticket-counter-day-2025-q1#TKT-2025-Q1-007:0000:e6a884abc6
- sop-supplier-bulletin-triage:0000:9620fe3cf5
- ticket-counter-day-2025-q1#TKT-2025-Q1-008:0000:e7786e66cc
- sop-r-410a-retrofit-customer-outreach:0000:2349bfb54c
- sop-warranty-claim-escalation:0000:f84fc045a9
- bulletin-r-454b-overview:0000:5abf4e6fa7
- bulletin-r-410a-phase-out-timeline:0000:ef1c9a2973
- email-lennox-partsplus-2024-12-12-rebate-program-028:0000:91840d0548
- spec-lennox-2025-condenser-pricebook-excerpt:0000:2675d0b6a1
synthesizer: deterministic
---

# Lennox

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

> # Lennox Technical Service Bulletin 2024-001

**Subject:** iComfort S30 thermostat — firmware update for intermittent
Wi-Fi disconnect after extended brownout events.

**Affected models:** 10F81 (iComfort S30 v1.x firmware). Production
dates 2022-06 through 2023-11. Serial range LCS22F-0001 through
LCS23K-9999.

**Severity:** Service — not safety.

## Symptom

Following an extended low-voltage eve… [bulletin-lennox-tsb-2024-001-icomfort:0000:854994a674]

> Ticket TKT-2025-Q1-007 (2025-02-24, customer CUS-0477)
manufacturer: Lennox | equipment_model: LEN997 | warehouse: WH-DAL

Notes: counter call — warranty status on LE-79082 purchased 26m ago. Followed up by email. [ticket-counter-day-2025-q1#TKT-2025-Q1-007:0000:e6a884abc6]

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

> Ticket TKT-2025-Q1-008 (2025-02-08, customer CUS-0449)
manufacturer: Lennox | equipment_model: LEN819 | warehouse: WH-CHI

Notes: training kit for A2L service — what's in it? [ticket-counter-day-2025-q1#TKT-2025-Q1-008:0000:e7786e66cc]

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

> # R-410A phase-out — operational timeline

Synthesized from the AIM Act Technology Transitions Rule, AHRI updates,
and OEM transition guides. For regulatory authority see
[[bulletins/epa-aim-act-summary]].

## Timeline

**Through 2024-12-31**
- R-410A residential and light-commercial AC/HP equipment may be
  manufactured and imported.
- Distributor inventory builds for the 2025 transition.

**2025… [bulletin-r-410a-phase-out-timeline:0000:ef1c9a2973]

> # Lennox PartsPlus — 2025 Loyalty rebate program — enrollment open

---

**From:** Pat Reyes <pat.reyes@lennoxpartsplus.example>
**To:** purchasing@graph-distributor.example
**Date:** 2024-12-12 10:26 EST
**Subject:** 2025 Loyalty rebate program — enrollment open

Enrollment is now open for the 2025 Loyalty program. Tier thresholds, accrual basis, and program-year boundaries are unchanged from 202… [email-lennox-partsplus-2024-12-12-rebate-program-028:0000:91840d0548]

> # Lennox 2025 Condenser Pricebook Excerpt

_Lennox · Lennox · Condenser_


| model | tonnage | refrigerant | list_price | tier_2_price |
|---|---|---|---|---|
| LEN469 | 2.5 | R-454B | 6031.00 | 5119.00 |
| LEN354 | 1.5 | R-454B | 3456.00 | 3619.00 |
| LEN618 | 2.5 | R-410A | 4211.00 | 2542.00 |
| LEN167 | 3.5 | R-454B | 5978.00 | 3373.00 |
| LEN836 | 2.5 | R-410A | 4056.00 | 3925.00 |
| LEN252 |… [spec-lennox-2025-condenser-pricebook-excerpt:0000:2675d0b6a1]

