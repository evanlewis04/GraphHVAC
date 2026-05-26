---
entity_type: manufacturers
entity_id: Trane
slug: trane
template_version: 2
template_name: manufacturer.md.j2
last_built: '2026-05-26T14:07:47+00:00'
source_chunks:
- email-trane-supply-2024-07-02-product-discontinuation-008:0000:fa3faaecba
- ticket-contractor-notes-2024-q3#TKT-2024-Q3-010:0000:693f5461f3
- sop-supplier-consolidation-post-mna:0000:014bd6862b
- ticket-warranty-claims-2024#TKT-MS-2024-002:0000:316c595b2e
- bulletin-trane-tsb-2024-002-r-32-launch:0000:d16e4c2761
- email-trane-supply-2024-04-22-price-increase-005:0000:527a7ef590
- sop-r-410a-retrofit-customer-outreach:0000:2349bfb54c
- bulletin-r-32-transition-overview:0000:29e90451bd
- ticket-warranty-claims-2024#TKT-MS-2024-007:0000:f3482ff171
- bulletin-r-454b-overview:0000:5abf4e6fa7
synthesizer: llm
---

# Trane

## Overview

Trane is a major U.S. HVAC OEM whose products appear across residential and commercial segments. The company distributes parts and equipment through its Trane Supply channel, which maintains active volume-tier and rebate programs relevant to distributors post-acquisition [sop-supplier-consolidation-post-mna:0000:014bd6862b]. Trane Supply has been an active correspondent on pricing and product lifecycle notices, including an 8% list price adjustment on its ControlBoard line effective 2024-05-10, attributed to raw material cost pressure on copper and aluminum [email-trane-supply-2024-04-22-price-increase-005:0000:527a7ef590].

For distributor procurement context, Trane Supply is grouped alongside [[manufacturers/carrier]], [[manufacturers/lennox]], and others as a major supplier where consolidated post-M&A volume should be leveraged for best-tier pricing [sop-supplier-consolidation-post-mna:0000:014bd6862b].

## Product Categories

Trane's catalog as seen through distributor interactions spans:

- **Residential heat pumps** — the 4TWR series is the primary platform. The 4TWR7 series runs on [[refrigerants/r-410a]] and was in end-of-life inventory burn-down as of 2024-Q4. The 4TWR8 series is the successor, built on [[refrigerants/r-454b]], with production starting 2024-Q3 for 2025 model year [bulletin-trane-tsb-2024-002-r-32-launch:0000:d16e4c2761].
- **Control boards** — the ControlBoard line is a tracked SKU category subject to its own pricing cycles [email-trane-supply-2024-04-22-price-increase-005:0000:527a7ef590].
- **RHE-series components** — the RHE283 series reached end-of-production 2024-08-23; replacement model RHE689 is in standard production. No new POs against RHE283 were accepted after 2024-08-09 [email-trane-supply-2024-07-02-product-discontinuation-008:0000:fa3faaecba].
- **TRA-series equipment models** — service tickets reference models TRA414, TRA780, and TRA462 across Atlanta and Charlotte warehouses, with fault code E21 appearing on multiple warranty claims [ticket-warranty-claims-2024#TKT-MS-2024-002:0000:316c595b2e][ticket-warranty-claims-2024#TKT-MS-2024-007:0000:f3482ff171][ticket-contractor-notes-2024-q3#TKT-2024-Q3-010:0000:693f5461f3].

Refrigerant charge specifications differ between the 4TWR7 and 4TWR8 platforms — for example, the 3-ton 4TWR7 carries 7 lb 0 oz of R-410A versus 7 lb 4 oz of [[refrigerants/r-454b]] in the 4TWR8 [bulletin-trane-tsb-2024-002-r-32-launch:0000:d16e4c2761]. The 4TWR8 cannot be retrofitted from R-410A; full system replacement (condenser, evaporator, line set flush, new TXV) is required [bulletin-trane-tsb-2024-002-r-32-launch:0000:d16e4c2761].

## Regulatory Posture

Trane is firmly in the [[refrigerants/r-454b]] camp for its 2025+ residential lines, alongside [[manufacturers/carrier]], [[manufacturers/lennox]], and [[manufacturers/bryant]] [bulletin-r-454b-overview:0000:5abf4e6fa7]. This positions Trane's product roadmap as a direct response to the [[regulations/aim-act]] phase-down of high-GWP refrigerants, with [[refrigerants/r-410a]] equipment being wound down in favor of A2L-rated platforms [bulletin-trane-tsb-2024-002-r-32-launch:0000:d16e4c2761][bulletin-r-32-transition-overview:0000:29e90451bd].

The 4TWR8 launch bulletin mandates A2L-compliant tooling for service: A2L-rated leak detectors (per UL 60335-2-40 §GG.6.2.4), A2L-rated digital manifold gauge sets, A2L-rated recovery machines with R-454B blend-preservation rating, and liquid-line charging hoses — vapor-charging from a virgin cylinder will fractionate the blend [bulletin-trane-tsb-2024-002-r-32-launch:0000:d16e4c2761]. These requirements flow directly to contractor training and distributor tool stocking obligations under the transition.

Distributor outreach on R-410A exposure should flag Trane's 4TWR8 as the replacement quote option for contractors with 4TWR7 installed base, given that retrofit is not a supported path [bulletin-trane-tsb-2024-002-r-32-launch:0000:d16e4c2761][sop-r-410a-retrofit-customer-outreach:0000:2349bfb54c].
