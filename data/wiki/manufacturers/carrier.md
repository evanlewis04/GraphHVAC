---
entity_type: manufacturers
entity_id: Carrier
slug: carrier
template_version: 1
template_name: manufacturer.md.j2
last_built: '2026-05-24T19:55:19+00:00'
source_chunks:
- bulletin-carrier-tsb-2024-007-fan-motor:0000:e5466c5030
- sop-supplier-bulletin-triage:0000:9620fe3cf5
- manual-synth-install-residential-condenser:0000:dc2822e656
- email-munch-s-supply-2025-05-11-delivery-delay-021:0000:08dc259392
- sop-supplier-consolidation-post-mna:0000:014bd6862b
- ticket-warranty-claims-2024#TKT-MS-2024-004:0000:aa4f4e47af
- email-carrier-enterprise-2024-12-12-delivery-delay-001:0000:ecf956daca
- ticket-counter-day-2025-q1#TKT-2025-Q1-001:0000:ae98210281
- email-lennox-partsplus-2024-05-18-delivery-delay-006:0000:1ea8eafe42
- bulletin-r-454b-overview:0000:5abf4e6fa7
synthesizer: llm
---

# Carrier

## Overview

Carrier is a major OEM of residential and commercial HVAC equipment. In the distributor context, Carrier products appear across equipment sales, warranty service, and parts counter activity. Carrier Enterprise is the primary wholesale distribution arm used for parts procurement, including control boards and other components [email-carrier-enterprise-2024-12-12-delivery-delay-001:0000:ecf956daca]. Warranty claims and counter tickets are logged against Carrier equipment models on a regular basis [ticket-warranty-claims-2024#TKT-MS-2024-004:0000:aa4f4e47af][ticket-counter-day-2025-q1#TKT-2025-Q1-001:0000:ae98210281]. Carrier Enterprise is listed among the major supplier relationships tracked through volume-tier and rebate programs during supplier consolidation activities [sop-supplier-consolidation-post-mna:0000:014bd6862b].

## Product Categories

Carrier's product footprint relevant to this distributor includes:

- **Residential condensers** — the 24ABC6 series (all tonnages, production 2021–current) is a documented active platform requiring parts support [bulletin-carrier-tsb-2024-007-fan-motor:0000:e5466c5030].
- **Condenser fan motors** — Carrier P/N HC39GE237 (supersedes obsolete HC39GE234) is the current service motor for the 24ABC6 series [bulletin-carrier-tsb-2024-007-fan-motor:0000:e5466c5030].
- **Control boards** — stocked and ordered through Carrier Enterprise; subject to lead-time variability (a 4-week delay on ControlBoard shipments out of Mexicali was documented in late 2024) [email-carrier-enterprise-2024-12-12-delivery-delay-001:0000:ecf956daca].
- **Contactors and electrical components** — referenced in warranty claims (e.g., contactor pull-in fault on model CAR499) [ticket-warranty-claims-2024#TKT-MS-2024-004:0000:aa4f4e47af].
- **2025+ A2L platforms** — Carrier is a primary adopter of R-454B as the refrigerant for U.S. residential AC and heat-pump equipment in 2025 and later model years [bulletin-r-454b-overview:0000:5abf4e6fa7].

## Regulatory Posture

Carrier is actively transitioning its residential equipment lines to R-454B (Opteon XL41 / Solstice 454B), a low-GWP (466 AR4) A2L-class refrigerant, as part of the U.S. HFC phasedown [bulletin-r-454b-overview:0000:5abf4e6fa7]. This makes Carrier one of the leading OEMs driving A2L compliance requirements at the field level. New Carrier A2L installations require technicians to observe UL 60335-2-40 charge limits, A2L-rated tools, and leak detector requirements [manual-synth-install-residential-condenser:0000:dc2822e656][bulletin-r-454b-overview:0000:5abf4e6fa7]. Liquid charging is mandatory on R-454B equipment to prevent fractionation — a critical service compliance point for counter staff to communicate [bulletin-r-454b-overview:0000:5abf4e6fa7].
