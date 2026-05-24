---
entity_type: procedures
entity_id: r-410a-retrofit-workflow
slug: r-410a-retrofit-workflow
template_version: 1
template_name: procedure.md.j2
last_built: '2026-05-24T19:56:02+00:00'
source_chunks:
- manual-synth-install-residential-condenser:0000:dc2822e656
- spec-carrier-2025-residential-condensers:0000:730402755b
- bulletin-trane-tsb-2024-002-r-32-launch:0000:d16e4c2761
- sop-refrigerant-pre-buy-guidance:0000:75588b7bfe
- sop-r-410a-retrofit-customer-outreach:0000:2349bfb54c
- bulletin-r-410a-phase-out-timeline:0000:ef1c9a2973
- bulletin-r-454b-overview:0000:5abf4e6fa7
- email-coastal-hvac-supply-2024-01-21-rebate-program-017:0000:f44bc5e123
- bulletin-epa-aim-act-summary:0000:2219085edc
- bulletin-r-32-transition-overview:0000:29e90451bd
- email-re-michel-2024-07-30-product-discontinuation-007:0000:473b5fbf7f
- spec-lennox-2025-condenser-pricebook-excerpt:0000:2675d0b6a1
synthesizer: llm
---

# r-410a-retrofit-workflow

## purpose

This workflow guides HVAC operations leads and contractor customers through replacing R-410A residential split-system equipment as the AIM Act phase-out takes effect. Starting January 1, 2025, new manufacture and import of R-410A residential AC and heat-pump equipment is prohibited under the EPA Technology Transitions Rule (GWP < 700 cutoff) [bulletin-epa-aim-act-summary:0000:2219085edc]. R-410A service refills remain legal, but bulk allowances compress to 60% of baseline through 2028 and 30% starting 2029, driving prices up 20–60% over the transition window [bulletin-r-410a-phase-out-timeline:0000:ef1c9a2973]. The retrofit workflow exists to move customers off R-410A equipment before service costs become unpassable.

---

## steps

### 1. Identify customer exposure

Run the R-410A exposure query against order history to flag contractor accounts with >$15K R-410A revenue in the trailing 24 months. Sort by descending exposure and keep the call list around 50 customers per region [sop-r-410a-retrofit-customer-outreach:0000:2349bfb54c].

### 2. Customer outreach

Contact targeted contractors with a proactive replacement-quote offer. Key talking points: the 2025-01-01 manufacture cutoff, year-over-year refill price increases (~18% already observed), and the tightening allowance schedule through 2028. Offer two actions: (1) pull SKU history and price R-32 or R-454B equivalents, or (2) pre-buy refill cylinders to lock 2024 pricing [sop-r-410a-retrofit-customer-outreach:0000:2349bfb54c].

### 3. Confirm replacement refrigerant and OEM path

Determine which low-GWP refrigerant applies to the replacement unit. Major OEM splits as of 2024-Q4:
- **R-454B:** Carrier, Trane, Lennox, Bryant [bulletin-r-454b-overview:0000:5abf4e6fa7]
- **R-32:** Daikin, Mitsubishi, parts of Goodman/Amana [bulletin-r-32-transition-overview:0000:29e90451bd]

**Critical:** R-410A systems cannot be retrofitted in place — the path for any R-410A unit requiring replacement is full system replacement (condenser + evaporator + line set flush + new TXV). There is no drop-in conversion [bulletin-trane-tsb-2024-002-r-32-launch:0000:d16e4c2761].

### 4. Site survey before pulling stock

- Confirm electrical service capacity for the new unit's MCA/MOP rating (most 2.0–5.0 ton residential condensers run 25–60A on 208/230V single-phase) [manual-synth-install-residential-condenser:0000:dc2822e656].
- For A2L units (R-454B or R-32), confirm room volume at the evaporator location meets UL 60335-2-40 charge limits [manual-synth-install-residential-condenser:0000:dc2822e656].
- Inspect the existing line set: reuse is permitted only if length is within OEM spec, the line set is free of moisture and acid, and it has been triple-flushed per OEM procedure [manual-synth-install-residential-condenser:0000:dc2822e656].

### 5. Verify technician tooling for A2L systems

Before dispatch, confirm the tech has A2L-rated equipment:
- A2L-rated leak detector (per UL 60335-2-40 §GG.6.2.4)
- A2L-rated digital manifold gauge set (required for charge weight verification)
- A2L-rated recovery machine with blend-preservation rating
- Liquid-line charging hose (3/8" SAE) — **mandatory** for R-454B; vapor-charging from a virgin cylinder will fractionate the blend [bulletin-trane-tsb-2024-002-r-32-launch:0000:d16e4c2761]

Mixing R-32 and R-410A in the same system destroys the system; strict bulk inventory separation is required at the counter [bulletin-r-32-transition-overview:0000:29e90451bd].

### 6. Mechanical installation

- Pad: level, 4" minimum thickness, 4" minimum clearance from exterior wall. Hurricane straps where required by code.
- Service clearance: 24" service-side, 12" airflow clearance on all other sides [manual-synth-install-residential-condenser:0000:dc2822e656].

### 7. Pressure test and evacuation

- Pressure test with **nitrogen** to OEM spec — typically 500–550 psig for R-410A legacy systems; 350–400 psig for R-454B systems. Hold 15 minutes; drop >5 psig fails.
- Triple evacuate to **500 microns** absolute. Standing vacuum test 10 minutes; drift must not exceed 1,000 microns. Failure indicates remaining moisture or leak [manual-synth-install-residential-condenser:0000:dc2822e656].

### 8. Charge by weight

Charge by weight using the OEM nameplate value. Note that R-454B charges differ from equivalent R-410A charges — for example, a 3.0-ton Trane unit requires 7 lb 0 oz R-410A vs. 7 lb 4 oz R-454B [bulletin-trane-tsb-2024-002-r-32-launch:0000:d16e4c2761]. R-454B **must** be charged as liquid to prevent fractionation [bulletin-r-454b-overview:0000:5abf4e6fa7].

### 9. Pre-buy refill inventory for residual R-410A service load

For customers maintaining existing R-410A units through the service window, offer pre-buy contracts capped at 18 months of trailing 24-month R-410A consumption or 200 25-lb cylinders, priced at spot +8%. Storage billing applies after month 2 at $0.85/cylinder/month [sop-refrigerant-pre-buy-guidance:0000:75588b7bfe].

---

## citations

| Chunk | Source |
|---|---|
| [bulletin-epa-aim-act-summary:0000:2219085edc] | AIM Act HFC phase-down — operational summary |
| [bulletin-r-410a-phase-out-timeline:0000:ef1c9a2973] | R-410A phase-out — operational timeline |
| [sop-r-410a-retrofit-customer-outreach:0000:2349bfb54c] | R-410A retrofit — customer outreach playbook |
| [bulletin-r-454b-overview:0000:5abf4e6fa7] | R-454B — replacement refrigerant overview |
| [bulletin-r-32-transition-overview:0000:29e90451bd] | R-32 — replacement refrigerant overview |
| [bulletin-trane-tsb-2024-002-r-32-launch:0000:d16e4c2761] | Trane TSB 2024-002: 4TWR8 / R-454B launch |
| [manual-synth-install-residential-condenser:0000:dc2822e656] | Residential split-system condenser — installation procedure |
| [sop-refrigerant-pre-buy-guidance:0000:75588b7bfe] | Refrigerant pre-buy guidance |
