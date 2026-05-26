---
entity_type: procedures
entity_id: warranty-claim-escalation
slug: warranty-claim-escalation
template_version: 2
template_name: procedure.md.j2
last_built: '2026-05-26T14:10:26+00:00'
source_chunks:
- sop-warranty-claim-escalation:0000:f84fc045a9
- sop-supplier-bulletin-triage:0000:9620fe3cf5
- bulletin-amana-tsb-2024-010-control-board-replacement:0000:d19a6155e1
- manual-synth-install-residential-condenser:0000:dc2822e656
- sop-supplier-consolidation-post-mna:0000:014bd6862b
- bulletin-york-tsb-2024-005-control-board-replacement:0000:c6422a1c4b
- ticket-counter-day-2025-q1#TKT-2025-Q1-009:0000:b87f1db753
- sop-supplier-rebate-tracking:0000:b6f847f568
- email-coastal-hvac-supply-2024-01-21-rebate-program-017:0000:f44bc5e123
- sop-credit-hold-procedure:0000:2d39107da4
- bulletin-r-454b-overview:0000:5abf4e6fa7
- ticket-contractor-notes-2024-q3#TKT-2024-Q3-008:0000:65c60494bd
synthesizer: llm
---

# warranty-claim-escalation

## purpose

This procedure governs how warranty claims from contractors are triaged, escalated, and resolved across three tiers — counter staff, service ops, and VP Operations. The goal is to protect contractor relationships, manage OEM warranty recovery, and limit unrecoverable cost exposure while maintaining clear accountability at each tier [sop-warranty-claim-escalation:0000:f84fc045a9].

---

## steps

### Tier 1 — Counter Staff (Day 0)

Counter staff or phone-line CSR receives the claim and assembles the standard claim packet [sop-warranty-claim-escalation:0000:f84fc045a9]:

- Original invoice (date, customer, SKU, serial #)
- Failure description from the contractor
- Photos of the failed part on installed equipment
- Service tech name and certification card #

If the SKU is within the OEM's standard warranty window **and** the failure mode matches a known manufacturer TSB, counter staff processes the swap directly. Replacement ships within 24 hours; SKU routes back to the manufacturer warranty pool [sop-warranty-claim-escalation:0000:f84fc045a9].

> **Example TSBs that qualify for direct Tier 1 swap:** The [[manufacturers/amana]] IFC control board (P/N AM-62867) for intermittent ignition failure on AMA460 furnaces carries a standard 5-year parts warranty [bulletin-amana-tsb-2024-010-control-board-replacement:0000:d19a6155e1]. Similarly, the [[manufacturers/york]] IFC control board (P/N YO-66065) for YOR386 furnaces carries the same 5-year coverage [bulletin-york-tsb-2024-005-control-board-replacement:0000:c6422a1c4b]. Both are direct-swap eligible at Tier 1 when a matching TSB is on file.

TSBs are routed to counter staff by Purchasing and filed under `data/sources/bulletins/` [sop-supplier-bulletin-triage:0000:9620fe3cf5].

---

### Tier 2 — Service Ops (Day 1–3)

Escalate to service ops if **any** of the following apply [sop-warranty-claim-escalation:0000:f84fc045a9]:

- SKU is **outside** the standard OEM warranty window but contractor claims extended-warranty coverage
- Failure mode is **not** documented in a manufacturer TSB
- Customer has had **>3** warranty claims for the same SKU in the same quarter
- Total claim value **>$2,500**

Service ops opens a formal OEM warranty case with photos and contractor install records and tracks it in the warranty log. Resolution SLAs [sop-warranty-claim-escalation:0000:f84fc045a9]:

| Outcome | SLA |
|---|---|
| Denial | 5 business days |
| Approval + ship | 10 business days |

---

### Tier 3 — VP Operations (Day 5+)

Escalate to VP Ops when the OEM denies a claim where the contractor has a strong case — for example, a TSB existed but was not communicated, or a known production-date defect is involved [sop-warranty-claim-escalation:0000:f84fc045a9].

VP Ops selects one of three resolutions [sop-warranty-claim-escalation:0000:f84fc045a9]:

1. **Eat the cost** internally to preserve the contractor relationship
2. **Push the OEM** via the regional rep; threaten allocation rebalance
3. **Decline the contractor**

Decision rule: most denials are absorbed internally if total exposure is **<$5K** and the customer's 24-month revenue exceeds **$50K** [sop-warranty-claim-escalation:0000:f84fc045a9].

---

## citations

| Chunk ID | Source | Relevance |
|---|---|---|
| [sop-warranty-claim-escalation:0000:f84fc045a9] | Warranty claim escalation SOP | Primary procedure — all three tiers |
| [sop-supplier-bulletin-triage:0000:9620fe3cf5] | Supplier bulletin triage SOP | TSB routing to counter staff |
| [bulletin-amana-tsb-2024-010-control-board-replacement:0000:d19a6155e1] | Amana TSB 2024-010 | Example Tier 1 direct-swap TSB |
| [bulletin-york-tsb-2024-005-control-board-replacement:0000:c6422a1c4b] | York TSB 2024-005 | Example Tier 1 direct-swap TSB |
