---
entity_type: manufacturers
entity_id: Mitsubishi
slug: mitsubishi
template_version: 2
template_name: manufacturer.md.j2
last_built: '2026-05-26T14:07:16+00:00'
source_chunks:
- bulletin-mitsubishi-tsb-2024-007-capacitor-batch-recall:0000:f00f8344b7
- ticket-contractor-notes-2024-q4#TKT-2024-Q4-007:0000:382fd3d58b
- ticket-contractor-notes-2024-q3#TKT-2024-Q3-008:0000:65c60494bd
- ticket-contractor-notes-2024-q4#TKT-2024-Q4-008:0000:a926af06a0
- ticket-contractor-notes-2024-q3#TKT-2024-Q3-001:0000:0b743e8da6
- ticket-contractor-notes-2024-q4#TKT-2024-Q4-003:0000:e903bee253
- bulletin-r-32-transition-overview:0000:29e90451bd
- ticket-counter-day-2025-q1#TKT-2025-Q1-004:0000:e6e603014c
synthesizer: llm
---

# Mitsubishi

## overview

Mitsubishi is a major HVAC OEM with an active parts footprint across multiple distributor warehouses, including WH-DAL, WH-ATL, and WH-CHA [ticket-contractor-notes-2024-q4#TKT-2024-Q4-007:0000:382fd3d58b][ticket-contractor-notes-2024-q4#TKT-2024-Q4-008:0000:a926af06a0][ticket-counter-day-2025-q1#TKT-2025-Q1-004:0000:e6e603014c]. Contractor inquiries cover multiple equipment model families (MIT612, MIT729, MIT782, MIT903, MIT921, MIT929), indicating a broad residential and light-commercial product range [ticket-contractor-notes-2024-q3#TKT-2024-Q3-008:0000:65c60494bd][ticket-contractor-notes-2024-q4#TKT-2024-Q4-003:0000:e903bee253]. Non-OEM cross-reference requests are frequent from the field, flagging ongoing demand for alternative sourcing on Mitsubishi-specific part numbers [ticket-contractor-notes-2024-q4#TKT-2024-Q4-007:0000:382fd3d58b][ticket-contractor-notes-2024-q4#TKT-2024-Q4-008:0000:a926af06a0][ticket-contractor-notes-2024-q3#TKT-2024-Q3-008:0000:65c60494bd].

A voluntary replacement program was issued in 2024 (TSB 2024-007) for a defective batch of 35 MFD / 440V dual-run capacitors (batch MI-94537) found 8–12% under rated capacitance, causing compressor hard-start and short-cycling in the field [bulletin-mitsubishi-tsb-2024-007-capacitor-batch-recall:0000:f00f8344b7]. Free replacements were available through end-of-quarter under standard RA return process, with full credit for any installed unit failing within 90 days and a standard 1-year warranty on replacements [bulletin-mitsubishi-tsb-2024-007-capacitor-batch-recall:0000:f00f8344b7].

## product_categories

Mitsubishi equipment models appearing in distributor tickets span at least six model designations (MIT612, MIT729, MIT782, MIT903, MIT921, MIT929), suggesting coverage across multiple tonnage classes and equipment types [ticket-contractor-notes-2024-q3#TKT-2024-Q3-001:0000:0b743e8da6][ticket-contractor-notes-2024-q3#TKT-2024-Q3-008:0000:65c60494bd][ticket-contractor-notes-2024-q4#TKT-2024-Q4-007:0000:382fd3d58b][ticket-contractor-notes-2024-q4#TKT-2024-Q4-008:0000:a926af06a0][ticket-counter-day-2025-q1#TKT-2025-Q1-004:0000:e6e603014c]. Parts activity includes run capacitors and other components with OEM part numbers in the MI-XXXXX format [bulletin-mitsubishi-tsb-2024-007-capacitor-batch-recall:0000:f00f8344b7][ticket-contractor-notes-2024-q4#TKT-2024-Q4-007:0000:382fd3d58b].

Contractors at WH-CHA have inquired about [[refrigerants/r-454b]] cylinder stock for Mitsubishi equipment, indicating some field usage or transition activity around that refrigerant [ticket-contractor-notes-2024-q4#TKT-2024-Q4-003:0000:e903bee253].

## regulatory_posture

Mitsubishi has adopted [[refrigerants/r-32]] as its primary low-GWP replacement for [[refrigerants/r-410a]] in U.S. residential AC and heat-pump equipment, aligning with [[manufacturers/daikin]] and parts of the [[manufacturers/goodman]] / [[manufacturers/amana]] lineup [bulletin-r-32-transition-overview:0000:29e90451bd]. This contrasts with [[manufacturers/carrier]], [[manufacturers/trane]], [[manufacturers/lennox]], and parts of [[manufacturers/rheem]] and [[manufacturers/york]], which have standardized on [[refrigerants/r-454b]] [bulletin-r-32-transition-overview:0000:29e90451bd].

R-32 carries an ASHRAE A2L (mildly flammable) classification, which drives charge limits per UL 60335-2-40 and additional installer training requirements [bulletin-r-32-transition-overview:0000:29e90451bd]. Distributors stocking Mitsubishi lines must maintain A2L-rated recovery equipment and leak detectors, and must strictly segregate R-32 bulk inventory from [[refrigerants/r-410a]] stock — mixing the two in the same system is a total system failure [bulletin-r-32-transition-overview:0000:29e90451bd]. The R-32 transition is driven by the [[regulations/aim-act]] low-GWP mandate; verify Mitsubishi's per-model refrigerant assignments on every supplier order through the transition period [bulletin-r-32-transition-overview:0000:29e90451bd].
