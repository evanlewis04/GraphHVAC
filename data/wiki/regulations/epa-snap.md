---
entity_type: regulations
entity_id: EPA-SNAP
slug: epa-snap
template_version: 2
template_name: regulation.md.j2
last_built: '2026-05-26T14:13:28+00:00'
source_chunks:
- bulletin-epa-aim-act-summary:0000:2219085edc
- bulletin-r-410a-phase-out-timeline:0000:ef1c9a2973
- bulletin-rheem-tsb-2024-004-thermostat-wifi-reconnect:0000:be8d51ddf1
- bulletin-goodman-tsb-2024-012-capacitor-batch-recall:0000:1feb570a29
- bulletin-r-32-transition-overview:0000:29e90451bd
- bulletin-amana-tsb-2024-010-control-board-replacement:0000:d19a6155e1
- bulletin-goodman-tsb-2024-003-inducer-motor-bearing:0000:24f0e85c6e
- bulletin-daikin-tsb-2024-006-ecm-blower-firmware:0000:3b7525377a
- bulletin-r-454b-overview:0000:5abf4e6fa7
- bulletin-honeywell-tsb-2024-011-ecm-blower-firmware:0000:903113f43b
synthesizer: llm
---

# EPA-SNAP

## Summary

EPA's Significant New Alternatives Policy (SNAP) program evaluates and regulates substitutes for ozone-depleting substances, including refrigerants used in HVAC equipment. In the context of current distributor operations, the most operationally significant regulatory action is the **Technology Transitions Rule** issued under the [[regulations/aim-act]], which sets GWP ceilings on refrigerants used in new equipment manufacture. [[refrigerants/r-410a]] (GWP ~2088) does not meet the sub-700 GWP threshold required for new residential and light-commercial equipment [bulletin-epa-aim-act-summary:0000:2219085edc]. Leading compliant replacements are [[refrigerants/r-454b]] (GWP ~466) and [[refrigerants/r-32]] (GWP ~675) [bulletin-epa-aim-act-summary:0000:2219085edc][bulletin-r-454b-overview:0000:5abf4e6fa7][bulletin-r-32-transition-overview:0000:29e90451bd].

The broader [[regulations/aim-act]] also phases down bulk HFC production and import allowances against a 2011–2013 baseline, compressing [[refrigerants/r-410a]] supply and driving up service-refill costs over time [bulletin-epa-aim-act-summary:0000:2219085edc].

_No source coverage for SNAP program history or the full listing of approved/unacceptable substitutes beyond what is noted above._

## Effective Dates

Key regulatory dates driven by the Technology Transitions Rule under the [[regulations/aim-act]] [bulletin-epa-aim-act-summary:0000:2219085edc][bulletin-r-410a-phase-out-timeline:0000:ef1c9a2973]:

| Date | Event |
|------|-------|
| Through 2024-12-31 | [[refrigerants/r-410a]] residential/light-commercial equipment may be manufactured and imported; distributor inventory builds |
| **2025-01-01** | New manufacture and import of [[refrigerants/r-410a]] residential AC and heat pump equipment prohibited (GWP < 700 cutoff) |
| 2025–2026 | [[refrigerants/r-410a]] bulk refrigerant prices expected to climb 20–60% as AIM Act allowances compress to 60% of baseline |
| **2026-01-01** | VRF equipment GWP < 700 cutoff phases in |
| 2025–2027 | Chillers and industrial process refrigeration: category-specific cutoff dates |
| 2029+ | Allowance cap drops to 30% of baseline; reclaimed-refrigerant programs take larger share of service supply |
| 2036+ | Long-term floor at 15% of baseline |

Service refills of [[refrigerants/r-410a]] in existing equipment remain legal after the 2025 manufacture cutoff [bulletin-epa-aim-act-summary:0000:2219085edc]. Distributor inventory on hand at 2024-12-31 may continue to be sold and installed [bulletin-r-410a-phase-out-timeline:0000:ef1c9a2973].

## Affected Equipment

**Residential and light-commercial AC and heat pumps** are the first and largest affected category, with new manufacture restricted to GWP < 700 refrigerants as of January 1, 2025 [bulletin-epa-aim-act-summary:0000:2219085edc]. OEM transition choices by platform [bulletin-r-454b-overview:0000:5abf4e6fa7][bulletin-r-32-transition-overview:0000:29e90451bd]:

- **[[refrigerants/r-454b]] adopters:** [[manufacturers/carrier]], [[manufacturers/trane]], [[manufacturers/lennox]], [[manufacturers/bryant]]; partial adoption by [[manufacturers/rheem]] and [[manufacturers/york]]
- **[[refrigerants/r-32]] adopters:** [[manufacturers/daikin]], [[manufacturers/mitsubishi]], [[manufacturers/goodman]], [[manufacturers/amana]]; some [[manufacturers/rheem]] and [[manufacturers/york]] lines

**Variable refrigerant flow (VRF):** GWP < 700 cutoff phases in by January 1, 2026 [bulletin-epa-aim-act-summary:0000:2219085edc].

**Chillers and industrial process refrigeration:** category-specific cutoff dates falling between 2025 and 2027 [bulletin-epa-aim-act-summary:0000:2219085edc].

**Existing equipment:** not directly affected by manufacture cutoffs. [[refrigerants/r-410a]] service refills remain legal; however, tightening allowances will pressure bulk supply costs progressively through the 2020s [bulletin-epa-aim-act-summary:0000:2219085edc][bulletin-r-410a-phase-out-timeline:0000:ef1c9a2973].

A2L-classified replacements ([[refrigerants/r-32]] and [[refrigerants/r-454b]]) require A2L-rated recovery machines, gauges, and leak detectors, plus installer training per UL 60335-2-40 [bulletin-r-32-transition-overview:0000:29e90451bd][bulletin-r-454b-overview:0000:5abf4e6fa7]. See [[procedures/r-410a-retrofit-workflow]] for distributor-side transition procedures.
