---
entity_type: manufacturers
entity_id: Daikin
slug: daikin
template_version: 1
template_name: manufacturer.md.j2
last_built: '2026-05-19T03:34:13+00:00'
source_chunks:
- bulletin-daikin-tsb-2024-006-ecm-blower-firmware:0000:3b7525377a
- sop-tariff-response-playbook:0000:48e5f73ab0
- bulletin-r-32-transition-overview:0000:29e90451bd
- sop-r-410a-retrofit-customer-outreach:0000:2349bfb54c
- ticket-contractor-notes-2024-q4#TKT-2024-Q4-002:0000:803b78f848
- ticket-warranty-claims-2024#TKT-MS-2024-003:0000:2dad4c447d
synthesizer: deterministic
---

# Daikin

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

## Product Categories

_No source coverage._

## Regulatory Posture

_No source coverage._

## Additional Source Material

> # Daikin Technical Service Bulletin 2024-006

Subject: ECM blower module on DAI409 platform — firmware update for low-airflow alarm.

Symptom: ECM blower posts low-airflow alarm code 21 on standard 0.5 in. WC static. Customers report unit running but reduced airflow at the registers.

Resolution: Apply firmware update DA-41307 via the OEM service tool (kit ST-FW-200). Update preserves dip-switch c… [bulletin-daikin-tsb-2024-006-ecm-blower-firmware:0000:3b7525377a]

> # Tariff response playbook

How we respond when a supplier announces a tariff-driven price change
or allocation cut. Owner: VP Operations. Last reviewed: 2024-Q1.

## When this triggers

Any of:

- A supplier email announces a price increase of >5% on a category we
  carry, attributed to tariffs (Section 232 steel/aluminum, Section
  301 China, anti-dumping, etc.).
- A supplier announces an alloca… [sop-tariff-response-playbook:0000:48e5f73ab0]

> # R-410A retrofit — customer outreach playbook

Owner: Sales Ops. Last reviewed: 2024-Q1. Driving doc:
[[bulletins/r-410a-phase-out-timeline]].

## Purpose

Reach contractor customers who carry high R-410A exposure with a
proactive replacement-quote offer **before** their installed base
starts hitting service costs they can't pass on.

## Identify the target list

Run the standard exposure query:… [sop-r-410a-retrofit-customer-outreach:0000:2349bfb54c]

> Ticket TKT-2024-Q4-002 (2024-11-30, customer CUS-0336)
manufacturer: Daikin | equipment_model: DAI585 | warehouse: WH-ATL

Notes: customer asked: is DA-57598 compatible with DAI585? [ticket-contractor-notes-2024-q4#TKT-2024-Q4-002:0000:803b78f848]

> Ticket TKT-MS-2024-003 (2024-11-05, customer CUS-0320)
manufacturer: Daikin | equipment_model: DAI196 | warehouse: WH-PHX | fault_code: E33 | parts_used: DA-44347

Notes: Contractor reports drain pan overflow — float switch tripped. Photos attached. Cert # 608-5892. [ticket-warranty-claims-2024#TKT-MS-2024-003:0000:2dad4c447d]

