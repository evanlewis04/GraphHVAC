---
entity_type: procedures
entity_id: warranty-claim-escalation
slug: warranty-claim-escalation
template_version: 1
template_name: procedure.md.j2
last_built: '2026-05-24T19:56:25+00:00'
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

## Purpose

Warranty claim escalation defines the path a warranty claim travels from initial counter receipt through OEM resolution, with clear ownership at each tier. The goal is to protect contractor relationships, recover OEM costs where possible, and avoid ad-hoc decisions. Owner: Customer Service [sop-warranty-claim-escalation:0000:f84fc045a9].

---

## Steps

### Tier 1 — Counter Staff (Day 0)

Counter staff or phone-line CSR receives the claim and assembles the standard claim packet [sop-warranty-claim-escalation:0000:f84fc045a9]:

- Original invoice (date, customer, SKU, serial #)
- Failure description from the contractor
- Photos of the failed part on installed equipment
- Service tech name and certification card #

If the SKU is within the OEM's standard warranty window **and** the failure mode matches a known manufacturer TSB, counter staff processes the swap directly. Replacement ships within 24 hours; SKU returns to the manufacturer warranty pool [sop-warranty-claim-escalation:0000:f84fc045a9].

TSBs are filed under `data/sources/bulletins/` by Purchasing and forwarded to counter staff upon receipt [sop-supplier-bulletin-triage:0000:9620fe3cf5]. Example on-file TSBs relevant to warranty swaps include the Amana IFC board bulletin (P/N AM-62867, 5-year parts warranty) [bulletin-amana-tsb-2024-010-control-board-replacement:0000:d19a6155e1] and the York IFC board bulletin (P/N YO-66065, 5-year parts warranty) [bulletin-york-tsb-2024-005-control-board-replacement:0000:c6422a1c4b].

---

### Tier 2 — Service Ops (Day 1–3)

Escalate to service ops if **any** of the following apply [sop-warranty-claim-escalation:0000:f84fc045a9]:

- SKU is outside the standard OEM warranty window but contractor claims extended-warranty coverage
- Failure mode is not documented in a manufacturer TSB
- Customer has had >3 warranty claims for the same SKU in the same quarter
- Total claim value exceeds $2,500

Service ops opens an OEM warranty case, attaches photos and contractor install records, and logs the claim in the warranty log. Resolution SLAs [sop-warranty-claim-escalation:0000:f84fc045a9]:

| Outcome | SLA |
|---|---|
| Denial | 5 business days |
| Approval + ship | 10 business days |

---

### Tier 3 — VP Operations (Day 5+)

Escalate to VP Ops if the OEM denies a claim where the contractor has a strong case — e.g., a TSB existed but was not communicated, or a known production-date defect is involved [sop-warranty-claim-escalation:0000:f84fc045a9].

VP Ops chooses one of three paths [sop-warranty-claim-escalation:0000:f84fc045a9]:

1. **Eat the cost** internally to preserve the contractor relationship
2. **Push the OEM** via the regional rep, with threat of allocation rebalance
3. **Decline the contractor**

Most denials are absorbed if total exposure is under $5K and the customer's 24-month revenue exceeds $50K [sop-warranty-claim-escalation:0000:f84fc045a9].

---

## Citations

| Chunk | Source |
|---|---|
| [sop-warranty-claim-escalation:0000:f84fc045a9] | Warranty claim escalation SOP — primary procedure document |
| [sop-supplier-bulletin-triage:0000:9620fe3cf5] | Supplier bulletin triage SOP — TSB routing and filing |
| [bulletin-amana-tsb-2024-010-control-board-replacement:0000:d19a6155e1] | Amana TSB 2024-010 — IFC board AM-62867 |
| [bulletin-york-tsb-2024-005-control-board-replacement:0000:c6422a1c4b] | York TSB 2024-005 — IFC board YO-66065 |
