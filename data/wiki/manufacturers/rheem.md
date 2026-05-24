---
entity_type: manufacturers
entity_id: Rheem
slug: rheem
template_version: 1
template_name: manufacturer.md.j2
last_built: '2026-05-24T19:54:35+00:00'
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

Rheem is a major HVAC OEM whose equipment spans residential and light-commercial applications. The brand is treated as a tier-1 manufacturer alongside Carrier, Trane, Lennox, Goodman, and York for purposes of tariff monitoring and price-list tracking [sop-tariff-response-playbook:0000:48e5f73ab0]. Rheem distributes equipment requiring R-410A, R-454B, and R-32 refrigerants across its current condenser lineup [spec-rheem-2025-r-454b-condensers:0000:bb87b1f4eb], reflecting an active transition away from R-410A.

## Product Categories

**Condensers:** Rheem's 2025 condenser catalog spans 2.0–5.0 ton units across three refrigerants — R-410A, R-454B, and R-32 — in the RHE-series platform [spec-rheem-2025-r-454b-condensers:0000:bb87b1f4eb]. Both low-GWP options are present, meaning distributors must stock R-454B and R-32 in parallel to cover Rheem installs [bulletin-r-32-transition-overview:0000:29e90451bd].

**Gas Furnaces / Air Handlers:** The RHE792 platform is a documented furnace or air-handler product with an inducer motor assembly subject to bearing wear under high-cycle or dirty-environment operation [bulletin-rheem-tsb-2024-013-inducer-motor-bearing:0000:29c0ae84bb]. The RHE286 platform carries an ECM blower module [bulletin-rheem-tsb-2024-001-ecm-blower-firmware:0000:a52fb5a5e4].

**Smart Thermostats:** Rheem offers the RHE101 Wi-Fi smart thermostat with cloud/app connectivity [bulletin-rheem-tsb-2024-004-thermostat-wifi-reconnect:0000:be8d51ddf1].

**Controls / Firmware:** Multiple platforms (RHE286 ECM blower, RHE101 thermostat) require OEM firmware tooling for field updates; Rheem issues Technical Service Bulletins to manage these [bulletin-rheem-tsb-2024-001-ecm-blower-firmware:0000:a52fb5a5e4][bulletin-rheem-tsb-2024-004-thermostat-wifi-reconnect:0000:be8d51ddf1].

## Regulatory Posture

Rheem has adopted a **split refrigerant strategy** for the post-R-410A transition: portions of the line use R-454B (GWP 466, A2L) and portions use R-32 (GWP 675, A2L), rather than committing entirely to one replacement [bulletin-r-454b-overview:0000:5abf4e6fa7][bulletin-r-32-transition-overview:0000:29e90451bd]. This is confirmed by the 2025 condenser catalog, which includes active SKUs in all three refrigerants [spec-rheem-2025-r-454b-condensers:0000:bb87b1f4eb].

Practical implication for distributors: Rheem contractors may call for either R-454B or R-32 depending on the specific model installed — verify refrigerant type per SKU on every order. A contractor sourcing R-454B 25-lb cylinders for a Rheem RHE150 was already noted in late 2024 [ticket-contractor-notes-2024-q4#TKT-2024-Q4-009:0000:fc69e53e57]. Both A2L refrigerants require A2L-rated recovery equipment, leak detectors, and installer training [bulletin-r-454b-overview:0000:5abf4e6fa7][bulletin-r-32-transition-overview:0000:29e90451bd].

Rheem's continued sale of R-410A condenser models in the 2025 catalog [spec-rheem-2025-r-454b-condensers:0000:bb87b1f4eb] means the installed base will generate R-410A service demand well into the back half of the decade, though refill pricing pressure increases as EPA allowances tighten through 2028 [sop-r-410a-retrofit-customer-outreach:0000:2349bfb54c].
