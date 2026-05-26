---
entity_type: manufacturers
entity_id: Carrier
slug: carrier
template_version: 2
template_name: manufacturer.md.j2
last_built: '2026-05-26T14:06:45+00:00'
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

## overview

Carrier is a major OEM of residential and commercial HVAC equipment, with a distribution network operating under the **Carrier Enterprise** branch supply banner. The company produces equipment across the split-system condenser, heat pump, and control board segments, among others [bulletin-carrier-tsb-2024-007-fan-motor:0000:e5466c5030][email-carrier-enterprise-2024-12-12-delivery-delay-001:0000:ecf956daca]. Carrier Enterprise is a named volume-tier supplier in consolidation conversations alongside [[manufacturers/lennox]], [[manufacturers/trane]], and others — meaning combined distributor volume can unlock better price tiers post-M&A [sop-supplier-consolidation-post-mna:0000:014bd6862b].

Carrier equipment is a recurring presence in warranty and counter tickets at the Atlanta warehouse (WH-ATL), covering models such as CAR179 and CAR499 [ticket-warranty-claims-2024#TKT-MS-2024-004:0000:aa4f4e47af][ticket-counter-day-2025-q1#TKT-2025-Q1-001:0000:ae98210281].

## product_categories

**Condensers:** The 24ABC6 series is a current residential split-system condenser line, spanning multiple tonnages with production dates from 2021 through present [bulletin-carrier-tsb-2024-007-fan-motor:0000:e5466c5030].

**Condenser fan motors:** Carrier P/N HC39GE237 is the current service replacement motor for the 24ABC6 series, superseding the obsolete HC39GE234. Aftermarket cross-references are available via [[manufacturers/us-motors]] equivalent listings [bulletin-carrier-tsb-2024-007-fan-motor:0000:e5466c5030].

**Control boards:** ControlBoard SKUs are stocked and distributed through Carrier Enterprise. Lead times are subject to supply disruption — a 4-week delay on ControlBoard shipments out of the Mexicali facility was reported in December 2024 [email-carrier-enterprise-2024-12-12-delivery-delay-001:0000:ecf956daca].

**Parts / accessories:** Run capacitors (typically 5 MFD for HC39GE237 applications) and terminal strip components are associated service parts for condenser repair [bulletin-carrier-tsb-2024-007-fan-motor:0000:e5466c5030]. Carrier part CA-74551 and CA-21709 appear as active SKUs in field tickets [ticket-warranty-claims-2024#TKT-MS-2024-004:0000:aa4f4e47af][ticket-counter-day-2025-q1#TKT-2025-Q1-001:0000:ae98210281].

## regulatory_posture

Carrier is one of the primary OEMs — alongside [[manufacturers/trane]] and [[manufacturers/lennox]] — that has committed [[refrigerants/r-454b]] as the platform refrigerant for U.S. residential AC and heat pump equipment in 2025+ model years [bulletin-r-454b-overview:0000:5abf4e6fa7]. [[manufacturers/bryant]], which shares platform lineage with Carrier, follows the same adoption path [bulletin-r-454b-overview:0000:5abf4e6fa7].

R-454B carries an ASHRAE A2L (mildly flammable) classification and a GWP of 466 versus 2088 for [[refrigerants/r-410a]], positioning Carrier's 2025+ line in compliance with the low-GWP trajectory driven by the [[regulations/aim-act]] [bulletin-r-454b-overview:0000:5abf4e6fa7]. New condenser installations for R-454B systems require attention to UL 60335-2-40 charge limits and minimum room volume requirements for the evaporator location [manual-synth-install-residential-condenser:0000:dc2822e656].

Technicians servicing Carrier A2L equipment must use leak detectors and A2L-rated tools, and must charge R-454B in liquid phase to prevent fractionation — this is noted as the most common service error during the refrigerant transition [bulletin-r-454b-overview:0000:5abf4e6fa7].
