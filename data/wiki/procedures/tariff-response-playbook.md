---
entity_type: procedures
entity_id: tariff-response-playbook
slug: tariff-response-playbook
template_version: 1
template_name: procedure.md.j2
last_built: '2026-05-24T19:56:51+00:00'
source_chunks:
- sop-supplier-bulletin-triage:0000:9620fe3cf5
- sop-price-book-update-procedure:0000:b0b51285b2
- sop-supplier-consolidation-post-mna:0000:014bd6862b
- email-re-michel-2024-07-30-product-discontinuation-007:0000:473b5fbf7f
- ticket-warranty-claims-2024#TKT-MS-2024-005:0000:f2ff669782
- email-carrier-tariff-passthrough-2025-03:0000:c1e7dd2120
- ticket-contractor-notes-2024-q3#TKT-2024-Q3-003:0000:9caf625514
- bulletin-epa-aim-act-summary:0000:2219085edc
- sop-supplier-rebate-tracking:0000:b6f847f568
- sop-top-customer-pricing-communication:0000:8fb4cc6cc8
- email-trane-supply-2024-04-22-price-increase-005:0000:527a7ef590
- ticket-warranty-claims-2024#TKT-MS-2024-006:0000:6f66251535
synthesizer: llm
---

# tariff-response-playbook

## Purpose

The tariff-response playbook standardizes the internal reaction whenever a supplier bulletin signals a pricing change—especially one attributed to tariffs. It is the shared SOP referenced by Purchasing, Operations, and Sales to ensure cost changes are absorbed, re-priced, and communicated consistently before the effective date. The playbook is triggered any time a bulletin is tagged `pricing`, `allocation`, or `tariff` in the purchasing inbox [sop-supplier-bulletin-triage:0000:9620fe3cf5], and also governs off-cycle price book updates outside the standard quarterly refresh [sop-price-book-update-procedure:0000:b0b51285b2].

## Steps

### Day 0 — Triage and tag

1. Purchasing assistant receives the bulletin at `purchasing@<our-domain>` (reviewed at 10 am and 3 pm daily) and applies the appropriate tag (`pricing`, `tariff`, or `allocation`) [sop-supplier-bulletin-triage:0000:9620fe3cf5].
2. If tagged `allocation`, VP Ops is flagged the same day [sop-supplier-bulletin-triage:0000:9620fe3cf5].
3. File the bulletin as a PDF or markdown under `data/sources/bulletins/` using the naming convention `supplier-<supplier>-<year>-<short-slug>.<md|pdf>` [sop-supplier-bulletin-triage:0000:9620fe3cf5].

### Day 0–effective date — Cost intake

1. Pull updated supplier costs into the staging table [sop-price-book-update-procedure:0000:b0b51285b2].
2. Identify the exact SKUs affected. For example, a Carrier tariff pass-through may cover specific model families (e.g., 24ABC6, 24ANB7, 25HCC5, partial 38MGRQ) while leaving others untouched [email-carrier-tariff-passthrough-2025-03:0000:c1e7dd2120]. Clarify any ambiguous SKU scope with the supplier rep before publishing [email-carrier-tariff-passthrough-2025-03:0000:c1e7dd2120].
3. Note any in-flight PO protection window the supplier offers (e.g., POs shipping before the effective date honored at the old price) [email-carrier-tariff-passthrough-2025-03:0000:c1e7dd2120].

### Price book update

1. Apply category margin policy to the updated costs and generate a proposed off-cycle price book [sop-price-book-update-procedure:0000:b0b51285b2].
2. Review with the sales and pricing committee, then publish to the ERP and counter terminals [sop-price-book-update-procedure:0000:b0b51285b2].
3. Log the update with: supplier bulletin source, SKUs affected, and effective date [sop-price-book-update-procedure:0000:b0b51285b2].

### Customer communication

1. **Same day** for tariff- and allocation-driven changes: account reps call top-25 customers (by 24-month revenue) directly, then follow up by email confirming effective date, magnitude, any substitute path, and an offer for a pre-buy at the old price if the customer has unfulfilled commitments [sop-top-customer-pricing-communication:0000:8fb4cc6cc8].
2. All remaining customers receive a bulletin email [sop-price-book-update-procedure:0000:b0b51285b2].
3. Log every customer conversation in the CRM with timestamp and customer reaction [sop-top-customer-pricing-communication:0000:8fb4cc6cc8].

## Citations

| Source | Relevance |
|---|---|
| [sop-supplier-bulletin-triage:0000:9620fe3cf5] | Inbox routing rules, tagging taxonomy, filing convention |
| [sop-price-book-update-procedure:0000:b0b51285b2] | Off-cycle price book mechanics, audit logging, customer broadcast |
| [sop-top-customer-pricing-communication:0000:8fb4cc6cc8] | Top-25 customer call-and-email protocol, CRM logging |
| [email-carrier-tariff-passthrough-2025-03:0000:c1e7dd2120] | Live example: Carrier Section 301 pass-through, SKU scoping, PO protection window |
