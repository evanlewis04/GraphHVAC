---
source_id: sop-warranty-claim-escalation
type: markdown
bucket: sops
title: "Warranty claim escalation"
issuer: Internal Ops
doc_date: 2023-11-08
license: synthetic-internal
---

# Warranty claim escalation

Owner: Customer Service. Last reviewed: 2023-Q4.

## Tier 1 — counter staff (Day 0)

Counter staff or phone-line CSR receives a warranty claim from a
contractor. Standard claim packet:

- Original invoice (date, customer, SKU, serial #).
- Failure description from the contractor.
- Photos of the failed part on installed equipment.
- Service tech name and certification card #.

If the SKU is in the OEM's standard warranty window and the failure
mode is a known issue from a manufacturer TSB (see
[[bulletins/]]), counter staff processes the swap directly. SKU
flows back to manufacturer warranty pool; replacement ships within
24h to the customer.

## Tier 2 — service ops (Day 1–3)

Escalate to service ops if any of:

- SKU is **outside** the standard OEM warranty window but the
  contractor claims extended-warranty coverage.
- Failure mode is **not** documented in a manufacturer TSB.
- Customer has had >3 warranty claims for the same SKU in the same
  quarter.
- Total claim value >$2,500.

Service ops opens an OEM warranty case with photos and the contractor's
install records. Track in the warranty log. Resolution SLA: 5 business
days for a denial; 10 business days for an approval and ship.

## Tier 3 — VP Operations (Day 5+)

Escalate to VP Ops if the OEM denies a claim where the contractor has a
strong case (e.g. manufacturer TSB existed but wasn't communicated;
known production-date defect). VP Ops decides:

- Eat the cost ourselves to preserve the contractor relationship.
- Push the OEM via the regional rep; threaten allocation re-balance.
- Decline the contractor.

Most denials at this level are eaten if total exposure < $5K and the
customer's 24-mo revenue > $50K. See [[concepts/top-customers-by-revenue]]
for the customer-value threshold list.

## What we DO NOT do

- Process warranty replacements on parts purchased through a competitor
  distributor. (Caught us out twice in 2022; service ops has the bad
  cases on file.)
- Issue credit for a contractor's labor unless explicitly contracted.
  Labor reimbursement is between the contractor and the OEM.
- Replace a SKU that has the wrong refrigerant for the customer's
  equipment without confirming the customer wasn't trying to retrofit.

## Common failure modes that hit warranty often

- Capacitors out of bag rated at < 90% of spec — bad supplier batch,
  see [[bulletins/mfr-carrier-tsb-2024-007-fan-motor]] for the
  cross-reference to the most common fan motor / capacitor pairing.
- Lennox iComfort S30 Wi-Fi loss after brownout — software, not a
  warranty replacement. See
  [[bulletins/mfr-lennox-tsb-2024-001-icomfort]].
- ECM blower modules with control-board incompatibility on older
  Goodman furnaces.

## Related

- [[sops/supplier-bulletin-triage]] — upstream identification of
  manufacturer-defect patterns.
