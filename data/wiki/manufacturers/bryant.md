---
entity_type: manufacturers
entity_id: Bryant
slug: bryant
template_version: 2
template_name: manufacturer.md.j2
last_built: '2026-05-26T14:08:32+00:00'
source_chunks:
- ticket-contractor-notes-2024-q3#TKT-2024-Q3-002:0000:9c86e28d3f
- bulletin-r-454b-overview:0000:5abf4e6fa7
- bulletin-bryant-tsb-2024-008-inducer-motor-bearing:0000:87189af649
- ticket-warranty-claims-2024#TKT-MS-2024-009:0000:d6801a3406
- ticket-warranty-claims-2024#TKT-MS-2024-001:0000:1b9cb72b8e
- sop-r-410a-retrofit-customer-outreach:0000:2349bfb54c
synthesizer: llm
---

# Bryant

## Overview

Bryant is an HVAC equipment manufacturer operating as a brand under [[manufacturers/carrier]], sharing platform designs and distribution infrastructure with the parent company. Bryant equipment appears across residential and commercial segments, including furnaces, condensing units, and heat pumps [bulletin-bryant-tsb-2024-008-inducer-motor-bearing:0000:87189af649][ticket-warranty-claims-2024#TKT-MS-2024-001:0000:1b9cb72b8e][ticket-warranty-claims-2024#TKT-MS-2024-009:0000:d6801a3406]. Field activity tracked through this distributor's ticket system references Bryant units across multiple warehouse regions, including WH-PHX, WH-CHI, and WH-CHA [ticket-contractor-notes-2024-q3#TKT-2024-Q3-002:0000:9c86e28d3f][ticket-warranty-claims-2024#TKT-MS-2024-001:0000:1b9cb72b8e][ticket-warranty-claims-2024#TKT-MS-2024-009:0000:d6801a3406].

## Product Categories

Bryant's documented equipment footprint in this vault spans:

- **Gas furnaces** — Model BRY832 appears in ignitor/IFC board warranty claims (fault code P-LOW, part BR-37693) [ticket-warranty-claims-2024#TKT-MS-2024-009:0000:d6801a3406].
- **Condensing/cooling units** — Model BRY228 involved in a condenser fan locked-rotor failure (part BR-21017) within five months of installation [ticket-warranty-claims-2024#TKT-MS-2024-001:0000:1b9cb72b8e].
- **Gas furnace air handlers with induced-draft combustion** — Model BRY743 subject to TSB 2024-008 for inducer motor bearing wear in dirty environments; corrective part is sealed-bearing variant BR-91412 [bulletin-bryant-tsb-2024-008-inducer-motor-bearing:0000:87189af649].
- **A2L-refrigerant equipment** — Model BRY308 referenced in contractor inquiries regarding A2L service training kits, indicating Bryant has units in the field or pipeline using [[refrigerants/r-454b]] or similar A2L refrigerants [ticket-contractor-notes-2024-q3#TKT-2024-Q3-002:0000:9c86e28d3f].

Standard warranty coverage observed on parts claims is **5-year parts** [bulletin-bryant-tsb-2024-008-inducer-motor-bearing:0000:87189af649]. See [[procedures/warranty-claim-escalation]] for claim handling.

## Regulatory Posture

Bryant is cited as a primary adopter of [[refrigerants/r-454b]] (A2L, GWP 466) for U.S. residential AC and heat-pump lines in 2025+ model years, alongside parent [[manufacturers/carrier]], [[manufacturers/trane]], and [[manufacturers/lennox]] [bulletin-r-454b-overview:0000:5abf4e6fa7]. This positions Bryant's equipment roadmap in direct alignment with [[regulations/aim-act]] phase-down requirements and the shift away from [[refrigerants/r-410a]].

Field contractors servicing Bryant A2L equipment must use A2L-rated tools, leak detectors, and complete applicable training [ticket-contractor-notes-2024-q3#TKT-2024-Q3-002:0000:9c86e28d3f][bulletin-r-454b-overview:0000:5abf4e6fa7]. Liquid charging is mandatory for R-454B — gaseous charging from a virgin cylinder will cause fractionation [bulletin-r-454b-overview:0000:5abf4e6fa7]. Refer to [[procedures/r-410a-retrofit-workflow]] for transition guidance on existing [[refrigerants/r-410a]] Bryant units in the installed base.
