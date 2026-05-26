---
entity_type: manufacturers
entity_id: Lennox
slug: lennox
template_version: 2
template_name: manufacturer.md.j2
last_built: '2026-05-26T14:08:13+00:00'
source_chunks:
- sop-supplier-bulletin-triage:0000:9620fe3cf5
- email-lennox-partsplus-2024-05-18-delivery-delay-006:0000:1ea8eafe42
- ticket-counter-day-2025-q1#TKT-2025-Q1-008:0000:e7786e66cc
- bulletin-r-32-transition-overview:0000:29e90451bd
- bulletin-lennox-tsb-2024-001-icomfort:0000:854994a674
- sop-r-410a-retrofit-customer-outreach:0000:2349bfb54c
- sop-supplier-consolidation-post-mna:0000:014bd6862b
- email-lennox-2025-q1-allocations:0000:848d0c2bdb
- email-lennox-partsplus-2024-12-12-rebate-program-028:0000:91840d0548
- spec-lennox-2025-condenser-pricebook-excerpt:0000:2675d0b6a1
synthesizer: llm
---

# Lennox

## Overview

Lennox is a major U.S. residential and light-commercial HVAC OEM and a key supplier relationship for this distributor. The commercial interface runs through **Lennox PartsPlus**, the parts distribution arm, with regional account managers handling allocation, pricing, and rebate program enrollment [email-lennox-partsplus-2024-12-12-rebate-program-028:0000:91840d0548][email-lennox-2025-q1-allocations:0000:848d0c2bdb]. Lennox PartsPlus is listed as one of the major suppliers considered during post-M&A consolidation exercises alongside [[manufacturers/carrier]], [[manufacturers/trane]], and others [sop-supplier-consolidation-post-mna:0000:014bd6862b].

Lennox publishes Technical Service Bulletins (TSBs) routed through the standard supplier bulletin triage process [sop-supplier-bulletin-triage:0000:9620fe3cf5]. A known active TSB covers the iComfort S30 smart thermostat — firmware v1.18.04 resolves intermittent Wi-Fi disconnect following brownout events; this is a service issue, not safety, and is not warranty-replacement eligible [bulletin-lennox-tsb-2024-001-icomfort:0000:854994a674].

## Product Categories

**Residential condensers** are the highest-volume category transacted with this distributor. The 2025 pricebook covers 1.5–5.0 ton units across three refrigerant families: [[refrigerants/r-454b]], [[refrigerants/r-410a]] (terminal inventory), and [[refrigerants/r-32]] [spec-lennox-2025-condenser-pricebook-excerpt:0000:2675d0b6a1]. Active 2025 model lines include the ML17XC1/ML18XC1 (R-454B) and XP25 heat pump (R-454B); R-410A finished goods are in terminal runout [email-lennox-2025-q1-allocations:0000:848d0c2bdb].

**Smart thermostats** — the iComfort S30 is a connected thermostat with cloud/app integration via the LennoxPros platform. Affected production units span 2022-06 through 2023-11 [bulletin-lennox-tsb-2024-001-icomfort:0000:854994a674].

**Motors** — sourced through Lennox PartsPlus; subject to periodic supply disruptions (a 2-week delay from the Charlotte facility was logged in May 2024 due to a freight carrier issue) [email-lennox-partsplus-2024-05-18-delivery-delay-006:0000:1ea8eafe42].

**A2L service training kits** — counter inquiries have been logged for Lennox equipment model LEN819 regarding A2L service kit contents, consistent with the refrigerant transition [ticket-counter-day-2025-q1#TKT-2025-Q1-008:0000:e7786e66cc].

## Regulatory Posture

Lennox has committed to [[refrigerants/r-454b]] as its primary [[refrigerants/r-410a]] replacement for the 2025 residential model year, aligned with the [[regulations/aim-act]] phase-down trajectory. The bulk of the residential condenser line transitioned to R-454B for 2025, with factory ramp underway at Stuttgart [email-lennox-2025-q1-allocations:0000:848d0c2bdb]. This places Lennox in the same R-454B camp as [[manufacturers/carrier]], [[manufacturers/trane]], and parts of [[manufacturers/rheem]] and [[manufacturers/york]] — as opposed to the R-32 path taken by [[manufacturers/daikin]], [[manufacturers/mitsubishi]], and parts of the [[manufacturers/goodman]]/[[manufacturers/amana]] lineup [bulletin-r-32-transition-overview:0000:29e90451bd].

R-410A SKUs remain in the pricebook but are terminal; only 62 finished-goods units were available as of January 2025 [email-lennox-2025-q1-allocations:0000:848d0c2bdb]. The 2025 R-454B price increase (3.5% effective 2025-02-01) was attributed to aluminum/Section 232 tariff pass-through plus a refrigerant cost component [email-lennox-2025-q1-allocations:0000:848d0c2bdb]. Counter staff should be prepared for A2L service questions on Lennox equipment as the installed base shifts [ticket-counter-day-2025-q1#TKT-2025-Q1-008:0000:e7786e66cc].
