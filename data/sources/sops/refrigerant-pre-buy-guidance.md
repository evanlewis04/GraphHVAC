---
source_id: sop-refrigerant-pre-buy-guidance
type: markdown
bucket: sops
title: "Refrigerant pre-buy guidance — 2024-Q4 through 2025"
issuer: Internal Ops
refrigerants: [R-410A, R-32, R-454B, R-22]
regulations: [AIM-Act]
doc_date: 2024-08-30
license: synthetic-internal
---

# Refrigerant pre-buy guidance

Owner: Inventory Ops. Last reviewed: 2024-Q3. Revisit 2025-Q1.

## Why this exists

The AIM Act allowance schedule compresses R-410A bulk supply through
2028. Contractors are asking us to stock more R-410A through the
transition; some are asking for pre-buy contracts. Goal of this SOP:
decide who to say yes to and how much to commit.

See [[bulletins/r-410a-phase-out-timeline]] and
[[bulletins/epa-aim-act-summary]] for the underlying schedule.

## R-410A pre-buy policy

**Eligible customers:** 24-month revenue > $50K AND
R-410A-tied revenue share > 30%. Pull the list:

```sql
SELECT
  c.id,
  c.name,
  SUM(o.extended_price) AS total_rev_24mo,
  SUM(CASE WHEN s.refrigerant = 'R-410A'
           THEN o.extended_price ELSE 0 END) AS r410a_rev_24mo
FROM orders o
JOIN skus s ON o.sku_id = s.id
JOIN customers c ON o.customer_id = c.id
WHERE o.order_date >= CURRENT_DATE - INTERVAL 24 MONTH
GROUP BY 1, 2
HAVING total_rev_24mo > 50000
   AND r410a_rev_24mo / NULLIF(total_rev_24mo, 0) > 0.30
ORDER BY r410a_rev_24mo DESC;
```

**Quantity limit:** maximum pre-buy is 18 months of the customer's
trailing 24-mo R-410A consumption, capped at 200 25-lb cylinders per
customer.

**Pricing:** today's spot + 8% (compensates for storage and capital
cost). Contract terms include monthly draw-downs to avoid concentrated
storage.

**Storage:** customer takes possession at our warehouse, billed
storage at $0.85/cylinder/month after month 2. We do not hold
unallocated inventory for pre-buy.

## R-32 / R-454B forward-buy policy

Forward buys on replacement refrigerants are **not** offered today
because supply is not constrained — pricing is high but not allocated.
Revisit if supplier allocation notices appear (none on file as of
2024-Q3).

## R-22 policy

R-22 ended new manufacture in 2020. Stock is reclaimed-only.

Pre-buy: not offered. Sell at spot. Refer customers with heavy R-22
exposure to the retrofit playbook —
[[sops/r-410a-retrofit-customer-outreach]] applies in spirit (substitute
the older R-22 → R-410A or R-32/R-454B conversation).

## Operational watch list

- Cylinder shortage: aluminum cylinder pricing is itself tariff-exposed
  (Section 232). Cylinder availability has lagged refrigerant supply by
  4–6 weeks in 2024. See [[emails/]] supplier-cylinder threads.
- Reclaimed refrigerant quality: only purchase from AHRI-700 certified
  suppliers; do not accept "service-grade" reclaimed without
  certification.

## Related

- [[bulletins/r-410a-phase-out-timeline]] — schedule.
- [[sops/r-410a-retrofit-customer-outreach]] — companion outreach SOP.
- [[sops/inventory-reorder-policy]] — general reorder mechanics.
