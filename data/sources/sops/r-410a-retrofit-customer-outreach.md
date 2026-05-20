---
source_id: sop-r-410a-retrofit-customer-outreach
type: markdown
bucket: sops
title: "R-410A retrofit — customer outreach playbook"
issuer: Internal Ops
refrigerants: [R-410A, R-32, R-454B]
regulations: [AIM-Act]
doc_date: 2024-03-12
license: synthetic-internal
---

# R-410A retrofit — customer outreach playbook

Owner: Sales Ops. Last reviewed: 2024-Q1. Driving doc:
[[bulletins/r-410a-phase-out-timeline]].

## Purpose

Reach contractor customers who carry high R-410A exposure with a
proactive replacement-quote offer **before** their installed base
starts hitting service costs they can't pass on.

## Identify the target list

Run the standard exposure query:

```sql
SELECT
  c.id AS customer_id,
  c.name,
  c.segment,
  c.region,
  SUM(o.extended_price) AS r410a_revenue_24mo
FROM orders o
JOIN skus s ON o.sku_id = s.id
JOIN customers c ON o.customer_id = c.id
WHERE s.refrigerant = 'R-410A'
  AND o.order_date >= CURRENT_DATE - INTERVAL 24 MONTH
GROUP BY 1, 2, 3, 4
HAVING SUM(o.extended_price) > 15000
ORDER BY r410a_revenue_24mo DESC;
```

Threshold ($15K) is set so the call list stays around 50 customers
per region. Adjust per the daily exec brief.

## Outreach template (residential contractors)

> Hey [Name], wanted to flag what we're seeing on R-410A.
>
> EPA's manufacture cutoff hits 2025-01-01 — equipment you can still
> install but no new units after the changeover. Service refills stay
> legal. What we're watching is refill pricing: it's already up 18%
> year-over-year and the allowance schedule tightens through 2028, so
> the back-half of any R-410A unit you install in 2024 is going to be
> expensive to service.
>
> Two things we can do:
>
> 1. Replacement quotes for your installed base — happy to pull the
>    SKU list of any R-410A equipment you've bought from us in the
>    last 5 years and price the R-32 or R-454B equivalents.
> 2. Pre-buy on refill cylinders if you want to lock 2024 pricing for
>    your 2025 service season.
>
> Want me to put together either of those?

For commercial contractors and property managers the messaging is the
same but emphasize TCO over 5 years, not single-unit replacement.

## Substitute path

When the customer asks "what do I install instead":

- For Carrier / Trane / Lennox / Bryant systems &rarr; recommend the
  R-454B model line. See [[bulletins/r-454b-overview]].
- For Goodman / Amana / Daikin systems &rarr; recommend R-32. See
  [[bulletins/r-32-transition-overview]].
- For Rheem / York &rarr; check the specific model year before
  recommending; both refrigerants are in their lineup.

Both replacement refrigerants are A2L-rated (mildly flammable). The
contractor will need A2L-rated leak detectors and a recovery machine.
We stock A2L starter kits — flag if they don't already have one.

## Quoting workflow

1. Pull the customer's last 24 months of R-410A SKU purchases.
2. For each SKU, identify the R-32 or R-454B equivalent from the same
   OEM. Use [[manufacturers/]] index for the crossover tables.
3. Generate a side-by-side quote: current R-410A unit price + projected
   refill cost over 5 years vs. R-32/R-454B unit price + projected
   refill cost over 5 years.
4. Include the A2L tool kit line item if the customer hasn't bought one
   in the last 18 months.

## What not to say

- "R-410A will be illegal" — false; service refills remain legal.
- "You have to convert now" — false; existing equipment can be serviced
  indefinitely.
- "Refill prices will stabilize" — unknown and contradicts the
  allowance schedule.

## Related

- [[bulletins/r-410a-phase-out-timeline]] — operational timeline.
- [[bulletins/r-32-transition-overview]], [[bulletins/r-454b-overview]]
  — replacement options.
- [[sops/refrigerant-pre-buy-guidance]] — companion SOP for the
  pre-buy half of the offer.
