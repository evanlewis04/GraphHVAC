---
entity_type: regulations
entity_id: AIM-Act
slug: aim-act
template_version: 2
template_name: regulation.md.j2
last_built: '2026-05-26T14:13:01+00:00'
source_chunks:
- bulletin-epa-aim-act-summary:0000:2219085edc
- bulletin-r-410a-phase-out-timeline:0000:ef1c9a2973
- bulletin-r-32-transition-overview:0000:29e90451bd
- bulletin-goodman-tsb-2024-003-inducer-motor-bearing:0000:24f0e85c6e
- bulletin-daikin-tsb-2024-006-ecm-blower-firmware:0000:3b7525377a
- bulletin-r-454b-overview:0000:5abf4e6fa7
- bulletin-honeywell-tsb-2024-011-ecm-blower-firmware:0000:903113f43b
- bulletin-mitsubishi-tsb-2024-007-capacitor-batch-recall:0000:f00f8344b7
- bulletin-heil-tsb-2024-009-thermostat-wifi-reconnect:0000:f5a4b1cf64
- bulletin-lennox-tsb-2024-001-icomfort:0000:854994a674
synthesizer: llm
---

# AIM-Act

## Summary

The American Innovation and Manufacturing (AIM) Act authorizes the EPA to phase down U.S. production and import of hydrofluorocarbon (HFC) refrigerants on a fixed allowance schedule. The baseline is average HFC consumption from 2011–2013. Allowances are auctioned and traded annually; manufacturers must hold allowances to produce or import bulk HFCs [bulletin-epa-aim-act-summary:0000:2219085edc].

Phase-down schedule vs. baseline:

| Period | Allowance |
|--------|-----------|
| 2022–2023 | 90% |
| 2024–2028 | 60% |
| 2029–2033 | 30% |
| 2034–2035 | 20% |
| 2036+ | 15% |

[bulletin-epa-aim-act-summary:0000:2219085edc]

Separate from the bulk phase-down, the EPA Technology Transitions Rule restricts the GWP of refrigerants permitted in **new** equipment by category and date. [[refrigerants/r-410a]] (GWP ~2088) does not qualify under the GWP < 700 threshold; primary replacements are [[refrigerants/r-454b]] (GWP ~466) and [[refrigerants/r-32]] (GWP ~675) [bulletin-epa-aim-act-summary:0000:2219085edc]. The rule is codified under 40 CFR Part 84 [bulletin-epa-aim-act-summary:0000:2219085edc].

Service refills of R-410A on existing equipment remain legal after the new-equipment manufacture cutoff, but allowance pressure will tighten supply and drive prices higher each year [bulletin-epa-aim-act-summary:0000:2219085edc][bulletin-r-410a-phase-out-timeline:0000:ef1c9a2973].

## Effective Dates

| Date | Event |
|------|-------|
| Through 2024-12-31 | R-410A residential/light-commercial AC and HP equipment may still be manufactured and imported; distributors build inventory ahead of transition [bulletin-r-410a-phase-out-timeline:0000:ef1c9a2973] |
| **2025-01-01** | New manufacture and import of R-410A residential AC and heat-pump equipment prohibited (GWP < 700 cutoff). Existing distributor inventory may continue to be sold and installed. New OEM model years ship in [[refrigerants/r-32]] or [[refrigerants/r-454b]] [bulletin-epa-aim-act-summary:0000:2219085edc][bulletin-r-410a-phase-out-timeline:0000:ef1c9a2973] |
| **2026-01-01** | VRF equipment GWP < 700 cutoff phases in [bulletin-epa-aim-act-summary:0000:2219085edc] |
| 2025–2027 | Chillers and industrial process refrigeration: category-specific cutoff dates [bulletin-epa-aim-act-summary:0000:2219085edc] |
| 2029 onward | Allowances drop to 30% of baseline; reclaimed-refrigerant programs expected to supply a larger share of service needs [bulletin-r-410a-phase-out-timeline:0000:ef1c9a2973] |

R-410A bulk-refrigerant prices are expected to climb 20–60% between 2025 and end of the 60%-allowance window (2028) as supply compresses [bulletin-r-410a-phase-out-timeline:0000:ef1c9a2973].

## Affected Equipment

**Residential and light commercial AC and heat pumps** — hardest hit. New manufacture restricted to GWP < 700 refrigerants from January 1, 2025. All major OEMs are transitioning platform refrigerants [bulletin-epa-aim-act-summary:0000:2219085edc]:

- [[manufacturers/carrier]], [[manufacturers/trane]], [[manufacturers/lennox]], [[manufacturers/bryant]] — transitioning to [[refrigerants/r-454b]] [bulletin-r-454b-overview:0000:5abf4e6fa7]
- [[manufacturers/daikin]], [[manufacturers/mitsubishi]], [[manufacturers/goodman]], [[manufacturers/amana]] — primarily adopting [[refrigerants/r-32]]; some R-454B SKUs in commercial lines [bulletin-r-32-transition-overview:0000:29e90451bd][bulletin-r-454b-overview:0000:5abf4e6fa7]
- [[manufacturers/rheem]], [[manufacturers/york]] — split adoption across R-32 and R-454B lines [bulletin-r-454b-overview:0000:5abf4e6fa7]

**Variable refrigerant flow (VRF)** — GWP < 700 cutoff phases in by January 1, 2026 [bulletin-epa-aim-act-summary:0000:2219085edc].

**Chillers and industrial process refrigeration** — category-specific compliance dates between 2025 and 2027 [bulletin-epa-aim-act-summary:0000:2219085edc].

**Existing equipment / service refills** — not subject to the new-equipment manufacture cutoff. [[refrigerants/r-410a]] refills remain legal but supply will tighten and cost will rise as AIM Act allowances compress year over year [bulletin-epa-aim-act-summary:0000:2219085edc][bulletin-r-410a-phase-out-timeline:0000:ef1c9a2973].

For the standard retrofit workflow on R-410A systems, see [[procedures/r-410a-retrofit-workflow]]. For refrigerant approval status under EPA programs, see [[regulations/epa-snap]].
