---
entity_type: procedures
entity_id: warranty-claim-escalation
slug: warranty-claim-escalation
template_version: 1
template_name: procedure.md.j2
last_built: '2026-05-19T03:33:19+00:00'
source_chunks:
- sop-warranty-claim-escalation:0000:f84fc045a9
- email-abco-distribution-2024-07-22-product-discontinuation-022:0000:bdb5a689ab
- email-goodin-company-2025-03-25-allocation-notice-027:0000:a7ac5cfce0
- ticket-contractor-notes-2024-q4#TKT-2024-Q4-002:0000:803b78f848
- bulletin-york-tsb-2024-005-control-board-replacement:0000:c6422a1c4b
- ticket-warranty-claims-2024#TKT-MS-2024-009:0000:d6801a3406
- ticket-contractor-notes-2024-q4#TKT-2024-Q4-009:0000:fc69e53e57
- ticket-warranty-claims-2024#TKT-MS-2024-004:0000:aa4f4e47af
- sop-credit-hold-procedure:0000:2d39107da4
- bulletin-goodman-tsb-2024-003-inducer-motor-bearing:0000:24f0e85c6e
- manual-synth-install-residential-condenser:0000:dc2822e656
- sop-supplier-rebate-tracking:0000:b6f847f568
synthesizer: deterministic
---

# warranty-claim-escalation

_This page was assembled without LLM synthesis (no `ANTHROPIC_API_KEY` or `--no-llm` was used). Content below is a structured list of supporting source chunks; set the API key and rebuild for narrative synthesis._

## Purpose

> # Warranty claim escalation

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
flows ba… [sop-warranty-claim-escalation:0000:f84fc045a9]

> # ABCO Distribution — End-of-life notice — YOR585 series

---

**From:** Pat Reyes <pat.reyes@abcodistribution.example>
**To:** purchasing@graph-distributor.example
**Date:** 2024-07-22 10:28 EST
**Subject:** End-of-life notice — YOR585 series

The YOR585 series will reach end-of-production on 2024-09-12. Terminal inventory will be allocated to active orders only; no new POs against YOR585 accepted after 2024-10-10. Replacement model YOR654 is now in standard production.

Thanks,
Pat Reyes
ABCO Distribution

--- [email-abco-distribution-2024-07-22-product-discontinuation-022:0000:bdb5a689ab]

## Steps

_No source coverage._

## Citations

_No source coverage._

## Additional Source Material

> # Warranty claim escalation

Owner: Customer Service. Last reviewed: 2023-Q4.

## Tier 1 — counter staff (Day 0)

Counter staff or phone-line CSR receives a warranty claim from a
contractor. Standard claim packet:

- Original invoice (date, customer, SKU, serial #).
- Failure description from the contractor.
- Photos of the failed part on installed equipment.
- Service tech name and certification… [sop-warranty-claim-escalation:0000:f84fc045a9]

> # ABCO Distribution — End-of-life notice — YOR585 series

---

**From:** Pat Reyes <pat.reyes@abcodistribution.example>
**To:** purchasing@graph-distributor.example
**Date:** 2024-07-22 10:28 EST
**Subject:** End-of-life notice — YOR585 series

The YOR585 series will reach end-of-production on 2024-09-12. Terminal inventory will be allocated to active orders only; no new POs against YOR585 accepte… [email-abco-distribution-2024-07-22-product-discontinuation-022:0000:bdb5a689ab]

> # Goodin Company — Q1 allocation update — Capacitor

---

**From:** Carlos Romero <carlos.romero@goodincompany.example>
**To:** purchasing@graph-distributor.example
**Date:** 2025-03-25 10:33 EST
**Subject:** Q1 allocation update — Capacitor

Our Capacitor capacity for Q1 is allocated at 11% of trailing-quarter volume across the channel. Your account allocation specifically: see attached. We expec… [email-goodin-company-2025-03-25-allocation-notice-027:0000:a7ac5cfce0]

> Ticket TKT-2024-Q4-002 (2024-11-30, customer CUS-0336)
manufacturer: Daikin | equipment_model: DAI585 | warehouse: WH-ATL

Notes: customer asked: is DA-57598 compatible with DAI585? [ticket-contractor-notes-2024-q4#TKT-2024-Q4-002:0000:803b78f848]

> # York Technical Service Bulletin 2024-005

Subject: YOR386 furnace IFC control board (P/N YO-66065) replacement procedure.

Symptom: intermittent ignition failure; status LED shows flash code 3 (pressure switch). Confirmed not to be a pressure switch failure — control board MOSFET drift on extended cycles.

Resolution: replace IFC board with YO-66065. Procedure: shut off gas, kill power, label al… [bulletin-york-tsb-2024-005-control-board-replacement:0000:c6422a1c4b]

> Ticket TKT-MS-2024-009 (2024-06-10, customer CUS-0261)
manufacturer: Bryant | equipment_model: BRY832 | warehouse: WH-CHI | fault_code: P-LOW | parts_used: BR-37693

Notes: Tech: no heat, ignitor flashing 3x — likely IFC board. Confirmed in field. Need warranty swap of BR-37693. [ticket-warranty-claims-2024#TKT-MS-2024-009:0000:d6801a3406]

> Ticket TKT-2024-Q4-009 (2024-12-03, customer CUS-0444)
manufacturer: Rheem | equipment_model: RHE150 | warehouse: WH-ATL

Notes: do you have 25-lb R-454B cylinders in stock at WH-ATL? [ticket-contractor-notes-2024-q4#TKT-2024-Q4-009:0000:fc69e53e57]

> Ticket TKT-MS-2024-004 (2024-10-28, customer CUS-0271)
manufacturer: Carrier | equipment_model: CAR499 | warehouse: WH-ATL | fault_code: LOCK | parts_used: CA-74551

Notes: intermittent humming at contactor pull-in. Within warranty? Bought 20 months ago. [ticket-warranty-claims-2024#TKT-MS-2024-004:0000:aa4f4e47af]

> # Credit hold procedure

Owner: Operations. Internal SOP.

## Section 1

Customer accounts move to credit hold when (a) any invoice ages > 60 days, (b) total AR exceeds approved credit limit, or (c) NSF/check-return event within 12 months.

## Section 2

Credit hold blocks new orders at the counter and through online ordering.

## Section 3

Sales rep is notified the same day. Customer must clear… [sop-credit-hold-procedure:0000:2d39107da4]

> # Goodman Technical Service Bulletin 2024-003

Subject: inducer motor on GOO823 — bearing wear after extended cycle counts.

Symptom: inducer motor audible bearing growl, progressing over 2-3 months, eventual lock-up. Affects units operating in dirty environments (commercial kitchens, agricultural).

Resolution: replace with sealed-bearing variant GO-62231. Customer is responsible for adding filtr… [bulletin-goodman-tsb-2024-003-inducer-motor-bearing:0000:24f0e85c6e]

> # Residential split-system condenser — installation procedure

Generic procedure used in our counter-day training material. Not a
substitute for the OEM install manual that ships with the unit. For
specific torque, charge, and clearance values consult the manufacturer
document — e.g.
[[bulletins/mfr-carrier-tsb-2024-007-fan-motor]] for fan-motor specs,
or the model-specific install IO sheet from t… [manual-synth-install-residential-condenser:0000:dc2822e656]

> # Supplier rebate tracking

Owner: Operations. Internal SOP.

## Section 1

Each supplier rebate program enrolled is recorded with: tier thresholds, accrual basis, payment cadence, program start and end dates, and our YTD volume against tier.

## Section 2

Monthly: AR-side rebate accrual is recorded as a contra-COGS entry per program.

## Section 3

Quarterly: reconcile booked accrual against the… [sop-supplier-rebate-tracking:0000:b6f847f568]

