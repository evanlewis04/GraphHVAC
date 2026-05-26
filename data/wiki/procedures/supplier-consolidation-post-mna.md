---
entity_type: procedures
entity_id: supplier-consolidation-post-mna
slug: supplier-consolidation-post-mna
template_version: 2
template_name: procedure.md.j2
last_built: '2026-05-26T14:11:32+00:00'
source_chunks:
- sop-supplier-consolidation-post-mna:0000:014bd6862b
- email-re-michel-2025-03-01-price-increase-020:0000:db819d4bf0
- sop-new-customer-onboarding:0000:674d0b015e
- bulletin-goodman-tsb-2024-003-inducer-motor-bearing:0000:24f0e85c6e
- email-lennox-partsplus-2024-07-05-rebate-program-013:0000:1829ed2a23
- sop-supplier-bulletin-triage:0000:9620fe3cf5
- email-coastal-hvac-supply-2024-01-21-rebate-program-017:0000:f44bc5e123
- sop-supplier-rebate-tracking:0000:b6f847f568
- ticket-contractor-notes-2024-q3#TKT-2024-Q3-005:0000:9194e5650d
- sop-seasonal-stocking-plan:0000:5936f6b934
- email-re-michel-2024-07-30-product-discontinuation-007:0000:473b5fbf7f
- sop-price-book-update-procedure:0000:b0b51285b2
synthesizer: llm
---

# supplier-consolidation-post-mna

## Purpose

When acquiring a regional distributor, this procedure drives the inherited supplier base down to a single consolidated list within 90 days of close. The goal is to align all combined purchasing volume onto the best price tiers, rebate programs, and payment terms available [sop-supplier-consolidation-post-mna:0000:014bd6862b].

Acquired distributors typically bring 6–15 supplier relationships, many overlapping with existing ones — but at different volume tiers, rebate enrollments, and contract terms. Left unmanaged, this fragments spend and forfeits leverage [sop-supplier-consolidation-post-mna:0000:014bd6862b].

---

## Steps

### Day 0–14 — Inventory the inherited supplier list

1. Pull the acquired company's last 12 months of purchase orders [sop-supplier-consolidation-post-mna:0000:014bd6862b].
2. For each supplier, capture: total spend, categories supplied, current price tier, rebate enrollment, payment terms, and any contracts in force [sop-supplier-consolidation-post-mna:0000:014bd6862b].
3. Tag every supplier into one of three buckets [sop-supplier-consolidation-post-mna:0000:014bd6862b]:
   - **Both** — already an existing supplier relationship.
   - **New** — relationship the acquired company has that we do not.
   - **Drop candidate** — single-line, low volume, replaceable.
4. Run combined-volume rebate eligibility checks against major suppliers. Named examples include [[manufacturers/lennox]] PartsPlus, [[manufacturers/carrier]] Enterprise, [[manufacturers/trane]] Supply, Johnstone Supply, and RE Michel — all of which have volume tiers that combined spend may now unlock [sop-supplier-consolidation-post-mna:0000:014bd6862b].

### Day 14–45 — Supplier conversations

Work through the three buckets in order [sop-supplier-consolidation-post-mna:0000:014bd6862b]:

1. **Both suppliers first.** Contact the regional rep, present the new combined volume, and negotiate up to the best available price tier. Confirm the new rate in writing [sop-supplier-consolidation-post-mna:0000:014bd6862b].
2. **New suppliers second.** Decide whether to retain (if the supplier provides category depth we want) or transition volume to an existing Both supplier. Suppliers being retained go through standard credit and onboarding [sop-supplier-consolidation-post-mna:0000:014bd6862b].
3. **Drop candidates last.** Wind down open POs and notify the supplier of intent to exit [sop-supplier-consolidation-post-mna:0000:014bd6862b].

> For new suppliers being onboarded, follow the credit application and approval flow documented in the new customer onboarding SOP (credit limits > $25K require CFO sign-off) [sop-new-customer-onboarding:0000:674d0b015e].

### Rebate program re-enrollment

Once supplier tiers are locked, re-enroll in rebate programs under the consolidated account. Record each program with tier thresholds, accrual basis, payment cadence, and YTD volume tracking per the rebate tracking SOP [sop-supplier-rebate-tracking:0000:b6f847f568]. Book the AR-side rebate accrual monthly as a contra-COGS entry and reconcile quarterly against supplier statements [sop-supplier-rebate-tracking:0000:b6f847f568].

Note that major programs (e.g., [[manufacturers/lennox]] PartsPlus Loyalty) have firm enrollment deadlines — confirm cutoff dates immediately on close [email-lennox-partsplus-2024-07-05-rebate-program-013:0000:1829ed2a23].

### Price book and bulletin hygiene

After consolidation, ensure the active supplier list in the ERP reflects only retained suppliers, and that incoming bulletins — pricing changes, allocations, TSBs — are routed through the standard supplier bulletin triage process [sop-supplier-bulletin-triage:0000:9620fe3cf5]. Off-cycle price changes from retained suppliers (e.g., a mid-year coil-line adjustment) should trigger the [[procedures/tariff-response-playbook]] day-0 steps and be logged with SKUs affected and effective date [sop-price-book-update-procedure:0000:b0b51285b2][email-re-michel-2025-03-01-price-increase-020:0000:db819d4bf0].

---

## Citations

| Chunk ID | Source |
|---|---|
| [sop-supplier-consolidation-post-mna:0000:014bd6862b] | Supplier consolidation post-M&A SOP — primary source |
| [sop-new-customer-onboarding:0000:674d0b015e] | New customer onboarding SOP — credit/approval flow for new suppliers |
| [sop-supplier-rebate-tracking:0000:b6f847f568] | Supplier rebate tracking SOP — program enrollment and accrual |
| [email-lennox-partsplus-2024-07-05-rebate-program-013:0000:1829ed2a23] | Lennox PartsPlus — 2025 Loyalty rebate enrollment deadline |
| [sop-supplier-bulletin-triage:0000:9620fe3cf5] | Supplier bulletin triage SOP — ongoing bulletin routing |
| [sop-price-book-update-procedure:0000:b0b51285b2] | Price book update procedure — off-cycle price change handling |
| [email-re-michel-2025-03-01-price-increase-020:0000:db819d4bf0] | RE Michel Q3 coil-line price adjustment — example off-cycle change |
