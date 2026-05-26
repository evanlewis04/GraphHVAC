---
entity_type: manufacturers
entity_id: Amana
slug: amana
template_version: 2
template_name: manufacturer.md.j2
last_built: '2026-05-26T14:04:32+00:00'
source_chunks:
- bulletin-amana-tsb-2024-010-control-board-replacement:0000:d19a6155e1
- ticket-counter-day-2025-q1#TKT-2025-Q1-005:0000:12bf609454
- ticket-contractor-notes-2024-q3#TKT-2024-Q3-009:0000:d26e149143
- ticket-contractor-notes-2024-q3#TKT-2024-Q3-004:0000:30abce54f6
- bulletin-r-32-transition-overview:0000:29e90451bd
- ticket-warranty-claims-2024#TKT-MS-2024-006:0000:6f66251535
- ticket-contractor-notes-2024-q4#TKT-2024-Q4-010:0000:0fd2f74a2a
- sop-r-410a-retrofit-customer-outreach:0000:2349bfb54c
- bulletin-r-454b-overview:0000:5abf4e6fa7
- ticket-contractor-notes-2024-q4#TKT-2024-Q4-001:0000:6a30587082
synthesizer: llm
---

# Amana

## Overview

Amana is a residential and light-commercial HVAC brand operating under the [[manufacturers/goodman]] family of companies. In the U.S. distributor channel, Amana equipment surfaces across multiple warehouse regions including WH-PHX, WH-DAL, and WH-ATL, with active ticket volume spanning furnaces, air handlers, and cooling equipment [ticket-contractor-notes-2024-q3#TKT-2024-Q3-009:0000:d26e149143][ticket-warranty-claims-2024#TKT-MS-2024-006:0000:6f66251535][ticket-contractor-notes-2024-q4#TKT-2024-Q4-001:0000:6a30587082]. Standard warranty on parts is 5 years [bulletin-amana-tsb-2024-010-control-board-replacement:0000:d19a6155e1].

Parts availability has been a recurring field issue; backorder situations on SKUs such as AM-48474 and AM-66203 have driven substitute-part inquiries from contractors [ticket-contractor-notes-2024-q4#TKT-2024-Q4-010:0000:0fd2f74a2a][ticket-contractor-notes-2024-q4#TKT-2024-Q4-001:0000:6a30587082].

## Product Categories

Amana's active equipment models in the distributor system span furnaces (AMA460, AMA532), air handlers/coils (AMA180, AMA184), and condensing/cooling units (AMA352, AMA415, AMA568) [bulletin-amana-tsb-2024-010-control-board-replacement:0000:d19a6155e1][ticket-contractor-notes-2024-q3#TKT-2024-Q3-004:0000:30abce54f6][ticket-warranty-claims-2024#TKT-MS-2024-006:0000:6f66251535][ticket-contractor-notes-2024-q4#TKT-2024-Q4-010:0000:0fd2f74a2a].

**Furnaces:** The AMA460 uses the AM-62867 IFC control board. A known field issue involves MOSFET drift on extended cycles, causing intermittent ignition failure (LED flash code 3). Resolution is board swap with dip-switch position verification across three ignition cycles [bulletin-amana-tsb-2024-010-control-board-replacement:0000:d19a6155e1].

**Cooling/Heat Pump:** The AMA568 has generated warranty activity around evaporator freeze-up (fault code P-LOW), typically traced to airflow restriction rather than refrigerant charge issues [ticket-warranty-claims-2024#TKT-MS-2024-006:0000:6f66251535].

**A2L-Ready Equipment:** Contractor inquiries regarding A2L service training kits have been logged against Amana models AMA184 and AMA532, indicating equipment in those lines is transitioning to A2L refrigerant platforms [ticket-counter-day-2025-q1#TKT-2025-Q1-005:0000:12bf609454][ticket-contractor-notes-2024-q3#TKT-2024-Q3-009:0000:d26e149143].

## Regulatory Posture

Amana, as part of the [[manufacturers/goodman]] group, is primarily adopting [[refrigerants/r-32]] for its residential lineup in response to [[regulations/aim-act]] phase-down requirements for [[refrigerants/r-410a]]. Some R-454B SKUs appear in the commercial line [bulletin-r-32-transition-overview:0000:29e90451bd][bulletin-r-454b-overview:0000:5abf4e6fa7].

[[refrigerants/r-32]] carries an A2L (mildly flammable) ASHRAE classification, which drives installer training requirements and mandates A2L-rated leak detectors and recovery equipment in confined spaces [bulletin-r-32-transition-overview:0000:29e90451bd]. The recurring contractor inquiries for A2L service training kits against Amana models confirm this transition is actively hitting the field [ticket-counter-day-2025-q1#TKT-2025-Q1-005:0000:12bf609454][ticket-contractor-notes-2024-q3#TKT-2024-Q3-009:0000:d26e149143].

For distributors, this means stocking [[refrigerants/r-32]] as the primary Amana-line replacement refrigerant while maintaining [[refrigerants/r-410a]] refill inventory for legacy service through the phase-down window. R-410A refill pricing has risen approximately 18% year-over-year and the allowance schedule tightens through 2028 [sop-r-410a-retrofit-customer-outreach:0000:2349bfb54c]. See also [[procedures/r-410a-retrofit-workflow]] for contractor outreach guidance during the transition.
