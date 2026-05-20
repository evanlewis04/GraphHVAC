---
source_id: sop-supplier-consolidation-post-mna
type: markdown
bucket: sops
title: "Supplier consolidation post-M&A"
issuer: Internal Ops
doc_date: 2024-01-22
license: synthetic-internal
---

# Supplier consolidation post-M&A

Owner: VP Operations. Last reviewed: 2024-Q1.

## Context

When we acquire a regional distributor, we typically inherit:

- 6–15 supplier relationships, often overlapping with our existing ones
- Different price tiers with the same supplier (their volume vs. ours)
- Different rebate program enrollments
- Different payment-term agreements
- Some "one-line" suppliers we don't want to keep

Goal of this SOP: reach one consolidated supplier list within 90 days
of close, with our combined volume on the best price tier we qualify for.

## Day 0–14 — inventory the inherited supplier list

1. Pull the acquired company's last 12 months of purchase orders.
2. For each supplier, capture: total spend, categories supplied, current
   price tier, rebate enrollment, payment terms, any contracts in force.
3. Cross-reference with our existing supplier list. Tag every supplier:
   - **Both** — we already buy from them.
   - **New** — they have a relationship we don't.
   - **Drop candidate** — single-line, low volume, replaceable.
4. Pull rebate-program eligibility on combined volume. Most major
   suppliers (Lennox PartsPlus, Carrier Enterprise, Trane Supply,
   Johnstone Supply, RE Michel) have volume tiers we may now qualify
   for.

## Day 14–45 — supplier conversations

Sequence:

1. **Both** suppliers first. Call the regional rep, share the new
   combined volume, ask to be moved to the best price tier on file.
   Lock the new rate in writing.
2. **New** suppliers second. Decide: keep (if they cover a category we
   want better depth in), or transition the volume to a Both supplier.
   New suppliers we want to keep get put through standard credit and
   onboarding.
3. **Drop candidates** last. Wind-down POs, notify the supplier of the
   intent to consolidate. No drama.

## Day 45–90 — operational cleanup

- Move all open POs to the consolidated supplier set.
- Reconcile rebate accruals (the acquired entity may have unbilled
  rebates due — chase them before they age out).
- Update the price book in the ERP. Cross-warehouse SKU mapping: any
  SKU the acquired entity carried under a different ID needs a unified
  ID. See [[sops/price-book-update-procedure]].
- Update [[concepts/supplier-concentration]] with the consolidated
  view.

## Watch-outs

- **Allocation risk.** Consolidating volume to one supplier may improve
  pricing but expose us to allocation cuts. Keep at least a secondary
  source on every category where we have >$500K annual spend.
- **Rebate program lockup.** Some suppliers tier rebates by enrollment
  date — moving to a new tier may reset accruals. Read the contract.
- **Contractor familiarity.** If the acquired entity's customers were
  used to a specific supplier branding (e.g. counter staff trained on
  Goodin vs. Munch's specs), retain that brand on counter signage
  through the first sales cycle.

## Most-recent consolidation events on file

- See [[emails/lennox-2025-q1-allocations]] — recent allocation event
  affecting our consolidated Lennox volume.

## Related

- [[concepts/supplier-concentration]] — current state metric.
- [[sops/price-book-update-procedure]] — ERP-side mechanics.
- [[sops/tariff-response-playbook]] — adjacent playbook when supplier
  pricing changes for non-M&A reasons.
