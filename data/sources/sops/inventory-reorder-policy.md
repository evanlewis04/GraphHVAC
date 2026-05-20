---
source_id: sop-inventory-reorder-policy
type: markdown
bucket: sops
title: Inventory reorder policy
issuer: Internal Ops
doc_date: 2023-11-30
license: synthetic-internal
---

# Inventory reorder policy

Owner: Operations. Internal SOP.

## Section 1

Reorder is triggered when on-hand quantity drops below the reorder point set per SKU.

## Section 2

Reorder points are recalculated quarterly based on the trailing 26 weeks of demand and a safety stock factor of 1.5× weekly demand for the cooling-season SKUs (May–Aug) and 1.2× for off-season SKUs.

## Section 3

Long-lead suppliers (ocean freight, > 6 weeks) carry a manual override per category set by purchasing.

## Section 4

Counter staff cannot bypass reorder points without VP Ops approval; emergency stock-out events are logged in the inventory exception log.

