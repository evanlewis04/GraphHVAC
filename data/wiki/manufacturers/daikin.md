---
entity_type: manufacturers
entity_id: Daikin
slug: daikin
template_version: 1
template_name: manufacturer.md.j2
last_built: '2026-05-24T19:53:42+00:00'
source_chunks:
- ticket-contractor-notes-2024-q4#TKT-2024-Q4-002:0000:803b78f848
- ticket-warranty-claims-2024#TKT-MS-2024-003:0000:2dad4c447d
- bulletin-r-32-transition-overview:0000:29e90451bd
- bulletin-daikin-tsb-2024-006-ecm-blower-firmware:0000:3b7525377a
- sop-r-410a-retrofit-customer-outreach:0000:2349bfb54c
- sop-tariff-response-playbook:0000:48e5f73ab0
synthesizer: llm
---

# Daikin

## Overview

Daikin is a major OEM in the U.S. HVAC market, recognized as one of the primary manufacturers tracked for pricing, allocation, and supply-chain events by distributor operations [sop-tariff-response-playbook:0000:48e5f73ab0]. The company has an established presence across residential and commercial equipment lines, with active service bulletin activity and field-support infrastructure including OEM service tools [bulletin-daikin-tsb-2024-006-ecm-blower-firmware:0000:3b7525377a].

## Product Categories

Daikin equipment in the distributor's active install base includes multiple platform models. Known platforms include:

- **DAI585** — referenced in active compatibility and parts inquiries [ticket-contractor-notes-2024-q4#TKT-2024-Q4-002:0000:803b78f848]
- **DAI196** — air-handler or fan-coil unit with drain pan and float switch assembly; fault code E33 associated with drain pan overflow events; parts DA-44347 used in warranty service [ticket-warranty-claims-2024#TKT-MS-2024-003:0000:2dad4c447d]
- **DAI409** — platform with ECM blower module; subject to low-airflow alarm (code 21) on standard 0.5 in. WC static; addressed via firmware update DA-41307 using service kit ST-FW-200 [bulletin-daikin-tsb-2024-006-ecm-blower-firmware:0000:3b7525377a]

## Regulatory Posture

Daikin is a long-standing R-32 adopter for U.S. residential AC and heat-pump equipment, making it one of the earlier OEM commitments to a low-GWP R-410A replacement [bulletin-r-32-transition-overview:0000:29e90451bd]. R-32 carries an A2L (mildly flammable) ASHRAE classification and a GWP of 675 versus R-410A's 2088, aligning Daikin's lineup with EPA AIM Act trajectory requirements [bulletin-r-32-transition-overview:0000:29e90451bd].

Distributor implications: Daikin's R-32 path diverges from R-454B adopters such as Carrier, Trane, and Lennox, requiring parallel refrigerant stocking and strict inventory separation to prevent cross-contamination [bulletin-r-32-transition-overview:0000:29e90451bd]. Contractors servicing Daikin equipment will require A2L-rated recovery machines, gauges, and leak detectors [bulletin-r-32-transition-overview:0000:29e90451bd].

Daikin is also on the monitored OEM list for out-of-cycle price-list updates tied to tariff events, triggering the distributor's tariff response playbook when such updates occur [sop-tariff-response-playbook:0000:48e5f73ab0].
