---
source_id: sop-price-book-update-procedure
type: markdown
bucket: sops
title: Price book update procedure
issuer: Internal Ops
doc_date: 2024-10-05
license: synthetic-internal
---

# Price book update procedure

Owner: Operations. Internal SOP.

## Section 1

Quarterly price book refresh is the primary cadence. Off-cycle updates triggered by supplier price changes follow the tariff playbook (see sops/tariff-response-playbook).

## Section 2

Mechanics: pull updated supplier costs into the staging table, apply category margin policy, generate the proposed price book, review with sales and pricing committee, publish to the ERP and the counter terminals.

## Section 3

Audit: every off-cycle update is logged with the supplier bulletin source, the SKUs affected, and the date of effect.

## Section 4

Customer comms: top-25 customers by 24-mo revenue receive direct rep contact; remainder receive the bulletin email.

