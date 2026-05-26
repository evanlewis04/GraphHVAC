---
entity_type: manufacturers
entity_id: Daikin
slug: daikin
template_version: 2
template_name: manufacturer.md.j2
last_built: '2026-05-26T14:09:13+00:00'
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

Daikin is a major HVAC original equipment manufacturer (OEM) tracked across distributor operations in residential and commercial equipment categories. The manufacturer appears in warehouse inventory across multiple distribution points, including WH-ATL and WH-PHX [ticket-contractor-notes-2024-q4#TKT-2024-Q4-002:0000:803b78f848][ticket-warranty-claims-2024#TKT-MS-2024-003:0000:2dad4c447d]. Daikin is listed alongside [[manufacturers/carrier]], [[manufacturers/trane]], [[manufacturers/lennox]], [[manufacturers/goodman]], [[manufacturers/rheem]], and [[manufacturers/york]] as a major OEM whose out-of-cycle price-list updates trigger the distributor's tariff response process [sop-tariff-response-playbook:0000:48e5f73ab0].

## Product Categories

Daikin equipment in the distributor catalog spans multiple platform families. Known models include the DAI585, DAI196, and DAI409 platforms [ticket-contractor-notes-2024-q4#TKT-2024-Q4-002:0000:803b78f848][ticket-warranty-claims-2024#TKT-MS-2024-003:0000:2dad4c447d][bulletin-daikin-tsb-2024-006-ecm-blower-firmware:0000:3b7525377a]. The DAI409 platform uses an ECM blower module; a known field issue (low-airflow alarm code 21 at standard 0.5 in. WC static) is resolved via firmware update DA-41307 using OEM service tool kit ST-FW-200, not parts replacement [bulletin-daikin-tsb-2024-006-ecm-blower-firmware:0000:3b7525377a]. The DAI196 has been associated with drain pan overflow / float switch trip faults in warranty claim activity [ticket-warranty-claims-2024#TKT-MS-2024-003:0000:2dad4c447d].

**Field note for warranty claims:** The DAI409 ECM firmware fix is explicitly **not** warranty-replacement-eligible — flag this during claim intake to avoid unnecessary parts dispatch [bulletin-daikin-tsb-2024-006-ecm-blower-firmware:0000:3b7525377a]. For escalation guidance, see [[procedures/warranty-claim-escalation]].

## Regulatory Posture

Daikin is a long-standing adopter of [[refrigerants/r-32]] for residential AC and heat pump equipment — one of the earliest U.S. OEM commitments to this refrigerant as a low-GWP replacement for [[refrigerants/r-410a]] [bulletin-r-32-transition-overview:0000:29e90451bd]. This distinguishes Daikin from [[manufacturers/carrier]], [[manufacturers/trane]], [[manufacturers/lennox]], and parts of [[manufacturers/rheem]] and [[manufacturers/york]], which have aligned to [[refrigerants/r-454b]] [bulletin-r-32-transition-overview:0000:29e90451bd]. [[manufacturers/mitsubishi]] and parts of the [[manufacturers/goodman]] / [[manufacturers/amana]] lineup share Daikin's R-32 path [bulletin-r-32-transition-overview:0000:29e90451bd].

R-32 carries an A2L (mildly flammable) ASHRAE classification, which has direct stocking and service implications: A2L-rated recovery equipment and leak detectors are required, and bulk R-32 inventory must be strictly separated from [[refrigerants/r-410a]] stock to prevent system-destroying cross-contamination [bulletin-r-32-transition-overview:0000:29e90451bd]. Distributor teams handling Daikin lines should ensure counter staff flag A2L tooling requirements at point of sale. The broader [[regulations/aim-act]] phase-down context drives urgency on contractor outreach for installed R-410A Daikin units; see [[procedures/r-410a-retrofit-workflow]] and [[procedures/tariff-response-playbook]] for operational response steps [sop-r-410a-retrofit-customer-outreach:0000:2349bfb54c][sop-tariff-response-playbook:0000:48e5f73ab0].
