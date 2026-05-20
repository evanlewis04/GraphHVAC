---
source_id: sop-tariff-response-playbook
type: markdown
bucket: sops
title: "Tariff response playbook"
issuer: Internal Ops
doc_date: 2024-02-01
license: synthetic-internal
---

# Tariff response playbook

How we respond when a supplier announces a tariff-driven price change
or allocation cut. Owner: VP Operations. Last reviewed: 2024-Q1.

## When this triggers

Any of:

- A supplier email announces a price increase of >5% on a category we
  carry, attributed to tariffs (Section 232 steel/aluminum, Section
  301 China, anti-dumping, etc.).
- A supplier announces an allocation reduction.
- A major OEM (Carrier, Trane, Lennox, Goodman, Rheem, York, Daikin)
  publishes a price-list update outside the normal Q1/Q3 cadence.

## Day 0 — within 4 hours of the bulletin

1. **Triage owner:** the bulletin should already be tagged per
   [[sops/supplier-bulletin-triage]] before it reaches the playbook.
2. **Pull exposure.** Query the staging DuckDB:

   ```sql
   -- Revenue at risk over the last 24 months for the affected category
   SELECT
     s.id AS sku_id,
     s.manufacturer,
     s.category,
     SUM(o.extended_price) AS revenue_24mo
   FROM orders o
   JOIN skus s ON o.sku_id = s.id
   WHERE s.manufacturer = :manufacturer
     AND s.category = :category
     AND o.order_date >= CURRENT_DATE - INTERVAL 24 MONTH
   GROUP BY 1, 2, 3
   ORDER BY revenue_24mo DESC;
   ```

3. **Identify top-N customers** for the affected SKUs. See
   [[concepts/top-customers-by-revenue]] for the pattern.
4. **Confirm substitute availability** for the affected category. See
   [[concepts/supplier-concentration]] for cross-supplier coverage.

## Day 1 — pricing decision

The pricing committee (VP Ops + CFO + sales lead) decides:

- **Pass-through:** if the increase is >7% and substitutes exist below
  the new price, we pass through immediately to protect margin.
- **Partial absorption:** if the increase is 3–7%, we typically absorb
  half through end-of-quarter to protect contractor relationships, then
  re-price.
- **Hold and review:** if the increase is <3% or affects <2% of revenue,
  we hold current pricing pending the next quarterly review.

In every case: document the decision in the pricing log and update the
ERP price book.

## Day 1–2 — customer communication

- **Top 25 customers by 24-mo revenue:** direct phone or email from
  their sales rep. Use the template at
  [[sops/top-customer-pricing-communication]].
- **All other customers:** bulletin email pushed via the standard
  contractor mailing list.
- **Counter day:** post a printed notice at each warehouse counter.

Never lead with the tariff as the reason. Lead with "manufacturer
adjustment, effective [date]" and offer the substitute. The tariff
attribution is for internal record only.

## Day 5 — internal review

- Confirm the ERP price book updated correctly across all warehouses.
- Confirm sales reps have logged customer conversations.
- Flag any customer with >$25K of exposure who has not responded for
  follow-up by the account manager.

## Examples on file

- See [[emails/lennox-2025-q1-allocations]] — recent tariff-adjacent
  allocation event.
- See [[emails/carrier-tariff-passthrough-2025-03]] — example of
  pass-through messaging.

## Related concepts

- [[bulletins/r-410a-phase-out-timeline]] — current macro pricing
  pressure context.
- [[sops/supplier-bulletin-triage]] — upstream of this playbook.
- [[concepts/supplier-concentration]] — substitute coverage analysis.
