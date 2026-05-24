---
entity_type: procedures
entity_id: supplier-consolidation-post-mna
slug: supplier-consolidation-post-mna
template_version: 1
template_name: procedure.md.j2
last_built: '2026-05-24T19:57:18+00:00'
source_chunks:
- sop-supplier-consolidation-post-mna:0000:014bd6862b
- email-re-michel-2025-03-01-price-increase-020:0000:db819d4bf0
- sop-new-customer-onboarding:0000:674d0b015e
- bulletin-goodman-tsb-2024-003-inducer-motor-bearing:0000:24f0e85c6e
- email-lennox-partsplus-2024-07-05-rebate-program-013:0000:1829ed2a23
- sop-supplier-bulletin-triage:0000:9620fe3cf5
- email-coastal-hvac-supply-2024-01-21-rebate-program-017:0000:f44bc5e123
- sop-supplier-rebate-tracking:0000:b6f847f568
- sop-seasonal-stocking-plan:0000:5936f6b934
- ticket-contractor-notes-2024-q3#TKT-2024-Q3-005:0000:9194e5650d
- email-re-michel-2024-07-30-product-discontinuation-007:0000:473b5fbf7f
- sop-price-book-update-procedure:0000:b0b51285b2
synthesizer: llm
---

# supplier-consolidation-post-mna

## Purpose

When acquiring a regional distributor, the goal is to reach one consolidated supplier list within 90 days of close, with combined volume placed on the best price tier available. The acquired company typically brings 6–15 supplier relationships, often overlapping with existing ones, along with differing price tiers, rebate enrollments, payment terms, and low-value "one-line" suppliers to be shed. [sop-supplier-consolidation-post-mna:0000:014bd6862b]

---

## Steps

### Day 0–14 — Inventory the inherited supplier list

1. Pull the acquired company's last 12 months of purchase orders. [sop-supplier-consolidation-post-mna:0000:014bd6862b]
2. For each supplier, capture: total spend, categories supplied, current price tier, rebate enrollment, payment terms, and any contracts in force. [sop-supplier-consolidation-post-mna:0000:014bd6862b]
3. Cross-reference against your existing supplier list and tag each supplier as one of: [sop-supplier-consolidation-post-mna:0000:014bd6862b]
   - **Both** — already an active relationship on your side.
   - **New** — relationship exists only on the acquired side.
   - **Drop candidate** — single-line, low volume, replaceable.
4. Pull rebate-program eligibility on combined volume. Major suppliers with volume tiers to reassess include Lennox PartsPlus, Carrier Enterprise, Trane Supply, Johnstone Supply, and RE Michel. [sop-supplier-consolidation-post-mna:0000:014bd6862b]

> **Note:** Each enrolled rebate program should be tracked with tier thresholds, accrual basis, payment cadence, and YTD volume against tier per the rebate tracking SOP. [sop-supplier-rebate-tracking:0000:b6f847f568]

---

### Day 14–45 — Supplier conversations

Work through supplier tags in this sequence: [sop-supplier-consolidation-post-mna:0000:014bd6862b]

1. **Both suppliers first.** Call the regional rep, present the new combined volume, and request placement on the best price tier on file. Get the new rate confirmed in writing.
2. **New suppliers second.** Decide whether to keep (if they provide category depth not covered by existing suppliers) or transition volume to a "Both" supplier. Suppliers retained through this step go through standard credit and onboarding. [sop-supplier-consolidation-post-mna:0000:014bd6862b]
   - Standard onboarding requires trade references (×3), bank reference, and a requested credit limit. Credits under $25K follow standard approval; above $25K requires CFO sign-off. [sop-new-customer-onboarding:0000:674d0b015e]
3. **Drop candidates last.** Wind down open POs and notify the supplier of the intent to discontinue the relationship. [sop-supplier-consolidation-post-mna:0000:014bd6862b]

---

### Ongoing — Rebate and pricing hygiene

- Re-enroll in rebate programs under the consolidated entity as needed. Rebate programs at major suppliers (e.g., Lennox PartsPlus) require enrollment by specific deadlines — confirm tier thresholds and program-year boundaries at time of re-enrollment. [email-lennox-partsplus-2024-07-05-rebate-program-013:0000:1829ed2a23]
- Any supplier price changes received during the consolidation window should be routed through the standard bulletin triage process (`pricing` tag → tariff-response-playbook day-0 steps). [sop-supplier-bulletin-triage:0000:9620fe3cf5]
- Price book updates triggered by renegotiated supplier costs follow the off-cycle update process: stage updated costs, apply category margin policy, review with pricing committee, and publish to ERP and counter terminals. [sop-price-book-update-procedure:0000:b0b51285b2]

---

## Citations

| Chunk ID | Source |
|---|---|
| [sop-supplier-consolidation-post-mna:0000:014bd6862b] | Supplier consolidation post-M&A SOP — primary procedure |
| [sop-supplier-rebate-tracking:0000:b6f847f568] | Supplier rebate tracking SOP |
| [sop-new-customer-onboarding:0000:674d0b015e] | New customer onboarding SOP (credit/onboarding flow) |
| [email-lennox-partsplus-2024-07-05-rebate-program-013:0000:1829ed2a23] | Lennox PartsPlus 2025 rebate enrollment email |
| [sop-supplier-bulletin-triage:0000:9620fe3cf5] | Supplier bulletin triage SOP |
| [sop-price-book-update-procedure:0000:b0b51285b2] | Price book update procedure SOP |
