---
entity_type: procedures
entity_id: r-410a-retrofit-workflow
slug: r-410a-retrofit-workflow
template_version: 2
template_name: procedure.md.j2
last_built: '2026-05-26T14:09:58+00:00'
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
validation_warnings:
- no_citations_in_body
---

# r-410a-retrofit-workflow

## Purpose

This workflow guides counter staff and field sales through the end-to-end process of replacing an [[refrigerants/r-410a]]-based residential split system with a compliant low-GWP replacement. The driver is the [[regulations/aim-act]] Technology Transitions Rule, which prohibits new manufacture of R-410A residential AC and heat-pump equipment effective January 1, 2025 [chunk_id: bulletin-epa-aim-act-summary:0000:2219085edc]. R-410A service refills remain legal, but allowance compression will push refill pricing 20–60% higher through 2028, making early system replacement the financially sound path for most customers [chunk_id: bulletin-r-410a-phase-out-timeline:0000:ef1c9a2973].

The outreach trigger: contractors who purchased more than $15K of R-410A equipment in the trailing 24 months are the priority conversion targets [chunk_id: sop-r-410a-retrofit-customer-outreach:0000:2349bfb54c].

---

## Steps

### 1. Identify the replacement refrigerant platform

Determine whether the replacement system will run [[refrigerants/r-454b]] or [[refrigerants/r-32]]. OEM choice drives the answer:

- **R-454B:** [[manufacturers/carrier]], [[manufacturers/trane]], [[manufacturers/lennox]], [[manufacturers/bryant]], parts of [[manufacturers/rheem]] and [[manufacturers/york]] [chunk_id: bulletin-r-454b-overview:0000:5abf4e6fa7]
- **R-32:** [[manufacturers/daikin]], [[manufacturers/mitsubishi]], parts of [[manufacturers/goodman]] and [[manufacturers/amana]] [chunk_id: bulletin-r-32-transition-overview:0000:29e90451bd]

Both replacements carry ASHRAE A2L (mildly flammable) classification, which drives tool and training requirements in all subsequent steps [chunk_id: bulletin-r-454b-overview:0000:5abf4e6fa7][chunk_id: bulletin-r-32-transition-overview:0000:29e90451bd].

### 2. Confirm the retrofit scope — full system replacement required

**R-410A systems cannot be retrofitted in place.** For example, [[manufacturers/trane]]'s 4TWR8 (R-454B) explicitly cannot be retrofitted from a 4TWR7 (R-410A); the required path is full system replacement: condenser + evaporator + line set flush + new TXV [chunk_id: bulletin-trane-tsb-2024-002-r-32-launch:0000:d16e4c2761]. Quote the customer accordingly.

### 3. Site survey

Before pulling stock [chunk_id: manual-synth-install-residential-condenser:0000:dc2822e656]:

- **Electrical:** confirm service capacity for the new unit's MCA/MOP rating (typically 25–60A, 208/230V single-phase for 2.0–5.0 ton residential).
- **Refrigerant compatibility:** A2L systems (R-454B, R-32) require minimum room volume for the evaporator location per UL 60335-2-40 charge limits.
- **Line set:** reuse is permitted only if lengths are within OEM spec, the line set is free of moisture and acid, and — for R-454B or R-32 — the line set is triple-flushed per OEM procedure.

### 4. Verify A2L tool readiness

Contractors must have A2L-rated equipment before any work begins [chunk_id: bulletin-trane-tsb-2024-002-r-32-launch:0000:d16e4c2761]:

- A2L-rated leak detector (per UL 60335-2-40 §GG.6.2.4)
- A2L-rated digital manifold gauge set (required for charge weight verification; mechanical gauges permitted for pressure checks only)
- A2L-rated recovery machine with blend-preservation rating
- Liquid-line charging hose (3/8" SAE) — **mandatory for R-454B**; vapor-charging from a virgin cylinder will fractionate the blend

The liquid-charging requirement is the single most common service mistake during the transition [chunk_id: bulletin-r-454b-overview:0000:5abf4e6fa7].

### 5. Mechanical installation

- Pad: level, 4" minimum thickness, 4" minimum clearance from exterior wall; hurricane straps per local code [chunk_id: manual-synth-install-residential-condenser:0000:dc2822e656].
- Service clearance: 24" on the service side, 12" airflow clearance on all other sides [chunk_id: manual-synth-install-residential-condenser:0000:dc2822e656].
- Tie-down per local code (typically two straps) [chunk_id: manual-synth-install-residential-condenser:0000:dc2822e656].

### 6. Pressure test and evacuation

- Pressure test with **nitrogen** to OEM-specified pressure. Typical targets: 500–550 psig for [[refrigerants/r-410a]] legacy systems; 350–400 psig for R-454B systems. Hold 15 minutes; a drop of more than 5 psig is a failure [chunk_id: manual-synth-install-residential-condenser:0000:dc2822e656].
- Triple evacuate to **500 microns** absolute. Standing vacuum test 10 minutes; drift exceeding 1,000 microns indicates remaining moisture or a leak [chunk_id: manual-synth-install-residential-condenser:0000:dc2822e656].

### 7. Charge by weight

Charge by weight per the OEM model-specific spec sheet. Note that R-454B charge weights differ from R-410A even on equivalent-tonnage platforms — for example, on [[manufacturers/trane]]'s 4TWR series, the R-454B charge runs 4–8 oz heavier per ton than the R-410A equivalent [chunk_id: bulletin-trane-tsb-2024-002-r-32-launch:0000:d16e4c2761]. Always pull the model-specific IO sheet; do not interpolate from the old unit's nameplate.

### 8. Refrigerant supply — stocking and pre-buy

- R-454B 25-lb cylinders are the standard distributor SKU through 2025; 100-lb returnable cylinders arrive mid-2025 from primary suppliers [chunk_id: bulletin-r-454b-overview:0000:5abf4e6fa7].
- R-410A service refill pre-buys are available for eligible customers (24-month revenue >$50K, R-410A revenue share >30%), capped at 18 months of trailing consumption or 200 cylinders, priced at spot +8% [chunk_id: sop-refrigerant-pre-buy-guidance:0000:75588b7bfe].
- Forward buys on R-32 or R-454B are **not** offered; supply is not currently constrained [chunk_id: sop-refrigerant-pre-buy-guidance:0000:75588b7bfe].

### 9. Customer communication

Use the standard outreach script to frame the economics: R-410A refill pricing is already up 18% year-over-year, and the allowance schedule tightens through 2028, making the back-half service costs of any remaining R-410A unit increasingly difficult to pass on [chunk_id: sop-r-410a-retrofit-customer-outreach:0000:2349bfb54c]. Offer replacement quotes cross-referenced against the customer's R-410A purchase history, and pair with a pre-buy option if they have in-service R-410A units they are not yet replacing.

---

## Citations

| Chunk | Source |
|---|---|
| [chunk_id: bulletin-epa-aim-act-summary:0000:2219085edc] | AIM Act HFC phase-down — operational summary |
| [chunk_id: bulletin-r-410a-phase-out-timeline:0000:ef1c9a2973] | R-410A phase-out — operational timeline |
| [chunk_id: sop-r-410a-retrofit-customer-outreach:0000:2349bfb54c] | R-410A
