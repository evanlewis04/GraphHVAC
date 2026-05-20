---
entity_type: manufacturers
entity_id: Rheem
slug: rheem
template_version: 1
template_name: manufacturer.md.j2
last_built: '2026-05-19T03:34:13+00:00'
source_chunks:
- bulletin-rheem-tsb-2024-013-inducer-motor-bearing:0000:29c0ae84bb
- ticket-contractor-notes-2024-q4#TKT-2024-Q4-009:0000:fc69e53e57
- bulletin-rheem-tsb-2024-004-thermostat-wifi-reconnect:0000:be8d51ddf1
- bulletin-r-32-transition-overview:0000:29e90451bd
- spec-rheem-2025-r-454b-condensers:0000:bb87b1f4eb
- bulletin-r-454b-overview:0000:5abf4e6fa7
- sop-r-410a-retrofit-customer-outreach:0000:2349bfb54c
- bulletin-rheem-tsb-2024-001-ecm-blower-firmware:0000:a52fb5a5e4
- sop-tariff-response-playbook:0000:48e5f73ab0
synthesizer: deterministic
---

# Rheem

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

> # Rheem Technical Service Bulletin 2024-013

Subject: inducer motor on RHE792 — bearing wear after extended cycle counts.

Symptom: inducer motor audible bearing growl, progressing over 2-3 months, eventual lock-up. Affects units operating in dirty environments (commercial kitchens, agricultural).

Resolution: replace with sealed-bearing variant RH-57386. Customer is responsible for adding filtrat… [bulletin-rheem-tsb-2024-013-inducer-motor-bearing:0000:29c0ae84bb]

> Ticket TKT-2024-Q4-009 (2024-12-03, customer CUS-0444)
manufacturer: Rheem | equipment_model: RHE150 | warehouse: WH-ATL

Notes: do you have 25-lb R-454B cylinders in stock at WH-ATL? [ticket-contractor-notes-2024-q4#TKT-2024-Q4-009:0000:fc69e53e57]

> # Rheem Technical Service Bulletin 2024-004

Subject: RHE101 smart thermostat — Wi-Fi auto-reconnect on router reboot.

Symptom: after a router restart or ISP-side network reset, thermostat does not auto-reconnect to Wi-Fi. HVAC control continues to function locally; remote app does not.

Resolution: firmware update RH-53514. OTA delivery to thermostats with active cloud connectivity; manual USB u… [bulletin-rheem-tsb-2024-004-thermostat-wifi-reconnect:0000:be8d51ddf1]

> # Rheem 2025 R 454B Condensers

_Rheem · Rheem · Condenser_


| model | tonnage | refrigerant | list_price | tier_2_price |
|---|---|---|---|---|
| RHE371 | 5.0 | R-454B | 4303.00 | 5536.00 |
| RHE491 | 5.0 | R-410A | 5594.00 | 2984.00 |
| RHE108 | 2.5 | R-410A | 2707.00 | 2746.00 |
| RHE282 | 3.0 | R-410A | 5222.00 | 2814.00 |
| RHE612 | 4.0 | R-410A | 5446.00 | 5245.00 |
| RHE290 | 3.5 | R-454B… [spec-rheem-2025-r-454b-condensers:0000:bb87b1f4eb]

> # R-410A retrofit — customer outreach playbook

Owner: Sales Ops. Last reviewed: 2024-Q1. Driving doc:
[[bulletins/r-410a-phase-out-timeline]].

## Purpose

Reach contractor customers who carry high R-410A exposure with a
proactive replacement-quote offer **before** their installed base
starts hitting service costs they can't pass on.

## Identify the target list

Run the standard exposure query:… [sop-r-410a-retrofit-customer-outreach:0000:2349bfb54c]

> # Rheem Technical Service Bulletin 2024-001

Subject: ECM blower module on RHE286 platform — firmware update for low-airflow alarm.

Symptom: ECM blower posts low-airflow alarm code 21 on standard 0.5 in. WC static. Customers report unit running but reduced airflow at the registers.

Resolution: Apply firmware update RH-15100 via the OEM service tool (kit ST-FW-200). Update preserves dip-switch co… [bulletin-rheem-tsb-2024-001-ecm-blower-firmware:0000:a52fb5a5e4]

> # Tariff response playbook

How we respond when a supplier announces a tariff-driven price change
or allocation cut. Owner: VP Operations. Last reviewed: 2024-Q1.

## When this triggers

Any of:

- A supplier email announces a price increase of >5% on a category we
  carry, attributed to tariffs (Section 232 steel/aluminum, Section
  301 China, anti-dumping, etc.).
- A supplier announces an alloca… [sop-tariff-response-playbook:0000:48e5f73ab0]

