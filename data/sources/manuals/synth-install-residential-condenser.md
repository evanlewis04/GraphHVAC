---
source_id: manual-synth-install-residential-condenser
type: markdown
bucket: manuals
title: "Residential split-system condenser installation — generic procedure"
issuer: Internal Training (synthetic)
doc_date: 2024-04-01
license: synthetic-internal
---

# Residential split-system condenser — installation procedure

Generic procedure used in our counter-day training material. Not a
substitute for the OEM install manual that ships with the unit. For
specific torque, charge, and clearance values consult the manufacturer
document — e.g.
[[bulletins/mfr-carrier-tsb-2024-007-fan-motor]] for fan-motor specs,
or the model-specific install IO sheet from the OEM.

## 1. Site survey

Before pulling stock for the install:

- Confirm electrical service capacity for the new unit's MCA / MOP
  rating. Most 2.0–5.0 ton residential condensers run 25–60A on
  208/230V single-phase.
- Confirm refrigerant compatibility. For R-454B and R-32 (A2L) systems,
  charge limits per UL 60335-2-40 require minimum room volume for the
  evaporator location. See
  [[bulletins/r-454b-overview]] §servicing concerns.
- Verify the existing line set diameter and length. Line set reuse is
  permitted if (a) lengths are within OEM spec, (b) line set is free
  of moisture and acid, (c) for R-454B/R-32, line set is triple-flushed
  per OEM procedure.

## 2. Mechanical

- Pad: level, 4" minimum thickness, 4" minimum clearance from the
  exterior wall. Hurricane straps in the relevant building-code
  jurisdictions.
- Service clearance: 24" service-side access, 12" airflow clearance on
  all other sides.
- Tie-down to pad per local code. Most jurisdictions require two
  straps.

## 3. Refrigerant

- Pressure test with **nitrogen** to OEM-specified pressure (typically
  500–550 psig for R-410A systems, 350–400 psig for R-454B systems).
  Hold 15 minutes. Drop > 5 psig fails.
- Triple evacuate to **500 microns** absolute. Standing vacuum
  test 10 minutes; do not exceed 1000 microns drift. Failure indicates
  remaining moisture or leak.
- Charge by weight (preferred) or by subcooling. **R-454B must be
  charged in liquid phase from the cylinder.** Vapor charging
  fractionates the blend; see [[bulletins/r-454b-overview]].

## 4. Electrical

- Service disconnect within sight of the unit, properly fused or
  breakered to MOP rating.
- 18 AWG control wire minimum for thermostat run. For runs > 100 ft
  use 16 AWG.
- Whip from disconnect to unit: liquid-tight flex, OEM-supplied or
  field-supplied per local code.
- Ground per NEC.

## 5. Startup

- Power-on sequence: thermostat to OFF, breaker on at panel, breaker on
  at disconnect, observe unit for ~60 seconds (some controls boards
  hold-off the compressor at startup). Then thermostat to COOL or HEAT.
- Verify:
  - Indoor blower starts before the outdoor unit (anti-frost-up).
  - Compressor amp draw within nameplate spec.
  - Suction line temperature drops within 90 seconds.
  - Subcooling and superheat within OEM range — typically 8–12 °F
    subcooling, 8–14 °F superheat at standard rating conditions.

## 6. Customer handoff

- Walk the homeowner through thermostat settings.
- Register the warranty with the OEM. Late registration (>60 days from
  install) drops the parts warranty from 10 years to 5 years on most
  OEMs.
- Leave the IO sheet, the warranty card, and our counter-day
  troubleshooting sheet with the homeowner.

## Common installation defects (training reference)

- **Service tech vapor-charged R-454B.** Most common single defect on
  the new platform. See [[bulletins/r-454b-overview]].
- **Triple-evac shortcut.** Single-pull evac to 500 microns without the
  nitrogen breaks. Passes the field gauge, fails the OEM warranty
  inspector if a refrigeration failure occurs in year one.
- **Fan-motor blade orientation reversed** during a fan replacement.
  See [[bulletins/mfr-carrier-tsb-2024-007-fan-motor]].
