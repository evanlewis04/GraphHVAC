---
entity_type: manufacturers
entity_id: Rheem
slug: rheem
template_version: 2
template_name: manufacturer.md.j2
last_built: '2026-05-26T14:05:54+00:00'
source_chunks:
- bulletin-rheem-tsb-2024-004-thermostat-wifi-reconnect:0000:be8d51ddf1
- bulletin-rheem-tsb-2024-013-inducer-motor-bearing:0000:29c0ae84bb
- ticket-contractor-notes-2024-q4#TKT-2024-Q4-009:0000:fc69e53e57
- bulletin-rheem-tsb-2024-001-ecm-blower-firmware:0000:a52fb5a5e4
- bulletin-r-32-transition-overview:0000:29e90451bd
- bulletin-r-454b-overview:0000:5abf4e6fa7
- spec-rheem-2025-r-454b-condensers:0000:bb87b1f4eb
- sop-r-410a-retrofit-customer-outreach:0000:2349bfb54c
- sop-tariff-response-playbook:0000:48e5f73ab0
synthesizer: llm
---

# Rheem

## Overview

Rheem is a major U.S. HVAC equipment manufacturer producing residential and light-commercial heating, cooling, and water-heating systems. Within this distributor's operations, Rheem is tracked as one of the primary OEM accounts alongside [[manufacturers/carrier]], [[manufacturers/trane]], [[manufacturers/lennox]], [[manufacturers/goodman]], [[manufacturers/york]], and [[manufacturers/daikin]] [sop-tariff-response-playbook:0000:48e5f73ab0]. Active field support includes multiple 2024 technical service bulletins covering firmware, motor, and connectivity issues across the RHE-series platform [bulletin-rheem-tsb-2024-001-ecm-blower-firmware:0000:a52fb5a5e4][bulletin-rheem-tsb-2024-013-inducer-motor-bearing:0000:29c0ae84bb][bulletin-rheem-tsb-2024-004-thermostat-wifi-reconnect:0000:be8d51ddf1].

## Product Categories

**Condensers**
Rheem's 2025 condenser lineup spans 2.0–5.0 ton and covers three refrigerant platforms — [[refrigerants/r-410a]], [[refrigerants/r-454b]], and [[refrigerants/r-32]] — simultaneously. Representative models include the RHE371 (5.0T, R-454B), RHE290 (3.5T, R-454B), RHE703 (2.5T, R-454B), RHE177 (2.5T, R-32), RHE348 (5.0T, R-32), and multiple R-410A carryover SKUs such as the RHE491, RHE108, and RHE612 [spec-rheem-2025-r-454b-condensers:0000:bb87b1f4eb].

**Air Handlers / Furnaces (RHE-series platforms)**
Field bulletins reference the RHE286 platform (ECM blower module) and RHE792 (inducer motor), indicating active gas furnace and air-handler lines in the current catalog [bulletin-rheem-tsb-2024-001-ecm-blower-firmware:0000:a52fb5a5e4][bulletin-rheem-tsb-2024-013-inducer-motor-bearing:0000:29c0ae84bb].

**Controls / Thermostats**
The RHE101 smart thermostat is an active SKU with cloud/app connectivity. TSB 2024-004 addresses a Wi-Fi auto-reconnect defect resolved via firmware update RH-53514; OTA delivery is supported for connected units, with manual USB update as fallback [bulletin-rheem-tsb-2024-004-thermostat-wifi-reconnect:0000:be8d51ddf1].

**Known Active Service Items**

| TSB | Platform | Issue | Resolution |
|-----|----------|-------|------------|
| 2024-001 | RHE286 ECM blower | Low-airflow alarm code 21 | Firmware RH-15100 via ST-FW-200 tool |
| 2024-013 | RHE792 inducer motor | Bearing wear/lock-up in dirty environments | Replace with sealed-bearing RH-57386 |
| 2024-004 | RHE101 thermostat | Wi-Fi no auto-reconnect post-router reboot | Firmware RH-53514, OTA or USB |

[bulletin-rheem-tsb-2024-001-ecm-blower-firmware:0000:a52fb5a5e4][bulletin-rheem-tsb-2024-013-inducer-motor-bearing:0000:29c0ae84bb][bulletin-rheem-tsb-2024-004-thermostat-wifi-reconnect:0000:be8d51ddf1]

## Regulatory Posture

Rheem is in a **split-platform transition** in response to the [[regulations/aim-act]] phase-down of high-GWP refrigerants. Unlike [[manufacturers/carrier]], [[manufacturers/trane]], and [[manufacturers/lennox]], which consolidated on [[refrigerants/r-454b]] as the primary replacement, Rheem is deploying both R-454B and [[refrigerants/r-32]] across its 2025 condenser lineup [bulletin-r-454b-overview:0000:5abf4e6fa7][spec-rheem-2025-r-454b-condensers:0000:bb87b1f4eb]. R-410A carryover SKUs remain in the active catalog as of the 2025 spec sheet [spec-rheem-2025-r-454b-condensers:0000:bb87b1f4eb].

The split means contractors and distributor buyers must verify refrigerant platform per model number before ordering service parts or refrigerant. Both R-454B and R-32 carry an A2L (mildly flammable) ASHRAE classification, requiring A2L-rated tools and leak detectors [bulletin-r-454b-overview:0000:5abf4e6fa7][bulletin-r-32-transition-overview:0000:29e90451bd]. R-454B additionally requires **liquid-phase charging** to prevent fractionation — the most common service error during the transition [bulletin-r-454b-overview:0000:5abf4e6fa7].

Contractor field requests for R-454B in 25-lb cylinders against Rheem RHE150 equipment have already been logged at WH-ATL (TKT-2024-Q4-009), confirming live demand against the new platform [ticket-contractor-notes-2024-q4#TKT-2024-Q4-009:0000:fc69e53e57]. See [[procedures/r-410a-retrofit-workflow]] for handling customers transitioning off existing R-410A Rheem units.
