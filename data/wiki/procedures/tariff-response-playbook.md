---
entity_type: procedures
entity_id: tariff-response-playbook
slug: tariff-response-playbook
template_version: 2
template_name: procedure.md.j2
last_built: '2026-05-26T14:11:02+00:00'
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

This playbook governs the distributor's response to any supplier communication signaling a tariff-driven price change. It is triggered automatically when the purchasing inbox routes a bulletin tagged `tariff` or `pricing`, or when an `allocation` flag is raised alongside a pricing event [sop-supplier-bulletin-triage:0000:9620fe3cf5]. The goal is to protect margin, communicate accurately with customers, and keep the price book current — all on a compressed timeline.

Off-cycle price book updates driven by supplier tariff pass-throughs are explicitly governed by this playbook; the quarterly refresh cadence does not apply in these cases [sop-price-book-update-procedure:0000:b0b51285b2].

Real-world example: [[manufacturers/carrier]] passed through a 4.2% increase effective 2025-03-17 on residential condenser, heat pump, and packaged unit lines tied to Section 301 China tariff increases, with updated price book delivered 2025-03-10 and in-flight POs honored at the old price through 2025-03-31 [email-carrier-tariff-passthrough-2025-03:0000:c1e7dd2120]. [[manufacturers/trane]] issued an 8% list price adjustment on the ControlBoard line in a similar off-cycle event [email-trane-supply-2024-04-22-price-increase-005:0000:527a7ef590].

---

## Steps

### Day 0 — Triage and flag

1. Purchasing assistant tags the bulletin `tariff` (or `pricing`/`allocation` as applicable) upon receipt during the 10 am or 3 pm inbox review [sop-supplier-bulletin-triage:0000:9620fe3cf5].
2. If the bulletin also carries an `allocation` tag, flag VP Ops same day — do not wait for the next scheduled touchpoint [sop-supplier-bulletin-triage:0000:9620fe3cf5].
3. Save the bulletin as a PDF or markdown under `data/sources/bulletins/` using the naming convention `supplier-<supplier>-<year>-<short-slug>.<md|pdf>` [sop-supplier-bulletin-triage:0000:9620fe3cf5].
4. Reply to the supplier rep to confirm receipt and request any outstanding details — effective date, exact SKU scope, whether in-flight POs are protected, and timing of any follow-on updates [email-carrier-tariff-passthrough-2025-03:0000:c1e7dd2120].

### Day 0–2 — Price book update

1. Pull the supplier's updated cost file into the staging table once it arrives (expect it 5–7 days before the effective date based on observed lead times) [email-carrier-tariff-passthrough-2025-03:0000:c1e7dd2120].
2. Apply category margin policy to the updated costs and generate a proposed price book [sop-price-book-update-procedure:0000:b0b51285b2].
3. Review proposed changes with the sales and pricing committee.
4. Publish to ERP and counter terminals before the supplier effective date [sop-price-book-update-procedure:0000:b0b51285b2].
5. Log the update with: supplier bulletin source, SKUs affected, and date of effect [sop-price-book-update-procedure:0000:b0b51285b2].

### Day 0–1 — Customer communication

1. Identify all top-25 customers (by 24-month revenue) who purchase the affected SKUs [sop-price-book-update-procedure:0000:b0b51285b2].
2. For tariff and allocation-driven changes, contact those customers **same day**: direct call from account rep, followed by a confirming email [sop-top-customer-pricing-communication:0000:8fb4cc6cc8].
3. Communication content must include: effective date, magnitude of change, any substitute path if one exists, and an offer for a pre-buy at the old price if the customer has unfulfilled commitments [sop-top-customer-pricing-communication:0000:8fb4cc6cc8].
4. Remaining customers receive a bulletin email [sop-price-book-update-procedure:0000:b0b51285b2].
5. Log every customer conversation in CRM with timestamp and customer reaction [sop-top-customer-pricing-communication:0000:8fb4cc6cc8].

### Ongoing — Rebate and tier implications

Review whether the tariff-driven cost shift affects rebate program tier calculations for the relevant supplier. Accrual entries may need adjustment; reconcile against the supplier's published statement within the normal 30-day dispute window [sop-supplier-rebate-tracking:0000:b6f847f568].

### Related workflows

- For refrigerant cost volatility intersecting tariff pressure (particularly [[refrigerants/r-410a]] under [[regulations/aim-act]] allowance tightening), cross-reference the [[procedures/r-410a-retrofit-workflow]] [bulletin-epa-aim-act-summary:0000:2219085edc].
- For supplier relationship changes following M&A that affect which supplier a tariff bulletin comes from, see [[procedures/supplier-consolidation-post-mna]] [sop-supplier-consolidation-post-mna:0000:014bd6862b].
- For warranty-related complications arising from parts substitutions made in response to tariff-driven SKU changes, see [[procedures/warranty-claim-escalation]].

---

## Citations

| Chunk ID | Source Document | Relevance |
|---|---|---|
| [sop-supplier-bulletin-triage:0000:9620fe3cf5] | Supplier bulletin triage SOP | Inbox routing rules, tagging taxonomy, filing convention |
| [sop-price-book-update-procedure:0000:b0b51285b2] | Price book update procedure | Off-cycle update mechanics, audit logging, customer comm scope |
| [sop-top-customer-pricing-communication:0000:8fb4cc6cc8] | Top customer pricing communication template | Same-day contact cadence, content requirements, CRM logging |
| [sop-supplier-rebate-tracking:0000:b6f847f568] | Supplier rebate tracking SOP | Accrual reconciliation triggered by cost changes |
| [email-carrier-tariff-passthrough-2025-03:0000:c1e7dd2120] | Carrier Enterprise tariff pass-through email, 2025-03 | Live example: 4.2% Section 301 pass-through, PO protection terms |
| [email-trane-supply-2024-04-22-price-increase-005:0000:527a7ef590] | Trane Supply Q4 price adjustment email, 2024-04 | Live example: 8% off-cycle list price increase |
| [sop-supplier-consolidation-post-mna:0000:014bd6862b] | Supplier consolidation post-M&A SOP | Context for inherited supplier pricing relationships |
| [bulletin-epa-aim-act-summary:0000:2219085edc] | AIM Act HFC phase-down operational summary | Regulatory cost pressure context for refrigerant SKUs |
