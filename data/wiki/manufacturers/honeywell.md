---
entity_type: manufacturers
entity_id: Honeywell
slug: honeywell
template_version: 2
template_name: manufacturer.md.j2
last_built: '2026-05-26T14:06:55+00:00'
source_chunks:
- bulletin-honeywell-tsb-2024-011-ecm-blower-firmware:0000:903113f43b
- ticket-warranty-claims-2024#TKT-MS-2024-008:0000:17c899e6c2
synthesizer: llm
---

# Honeywell

## Overview

Honeywell is a major HVAC controls and components manufacturer supplying the commercial and residential HVAC industry. Product lines include ECM blower modules, contactors, and associated controls hardware. Known vault cross-references include integration points with equipment from [[manufacturers/carrier]], [[manufacturers/trane]], [[manufacturers/lennox]], and other OEM platforms. Field support is handled through technical service bulletins (TSBs) and firmware update toolkits distributed to distributors and technicians.

Notable recent field activity includes a firmware fix for the HON255 platform ECM blower module addressing low-airflow alarm code 21 at standard 0.5 in. WC static; resolution is applied via update HO-85004 using service kit ST-FW-200, estimated at 8 minutes per unit [bulletin-honeywell-tsb-2024-011-ecm-blower-firmware:0000:903113f43b]. Warranty replacement is not applicable for this issue — firmware-only fix [bulletin-honeywell-tsb-2024-011-ecm-blower-firmware:0000:903113f43b].

## Product Categories

Honeywell's documented product presence in this vault covers:

- **ECM Blower Modules** — HON255 platform; subject to firmware field updates [bulletin-honeywell-tsb-2024-011-ecm-blower-firmware:0000:903113f43b]
- **Contactors** — part HO-41020, as referenced in warranty claim activity on model HON772 [ticket-warranty-claims-2024#TKT-MS-2024-008:0000:17c899e6c2]

No additional product category coverage is available from current source chunks. Honeywell's broader catalog (thermostats, ignition controls, gas valves) is not yet sourced in this vault. Note that [[manufacturers/emerson]] and [[manufacturers/white-rodgers]] overlap competitively in controls segments.

## Regulatory Posture

_No source coverage._
