# Entity & Workflow Mapping — HVAC Distributor → Club Portfolio (Invited)

This is a **translation layer, not a rebuild**. The HVAC distributor stays
the working proof-of-concept: same DuckDB schema, same workflows, same
citation-grounded agent loop, same eval numbers. This doc exists so a
club-portfolio audience can see themselves in the existing architecture
without us re-skinning any code before the meeting.

## Entity mapping

Grounded in the actual dataclasses in `src/ingest/synthetic.py`:

| HVAC entity (as built) | Fields | Club-portfolio equivalent |
|---|---|---|
| `Warehouse{id, name, state}` | distribution center + state | Club location (property + state) |
| `Supplier{id, name, is_master, primary_category}` | vendor + master-distributor flag + category | Vendor / F&B supplier (category, preferred-vendor flag) |
| `Customer{id, name, segment, region, primary_warehouse_id}` | segment (Residential/Commercial Contractor, Property Manager, Builder), region, home warehouse | Member / member segment (e.g. Full Golf, Social, Corporate), region, home club |

The relationships don't change: a `Customer` still rolls up to one
`Warehouse` and buys `SKU`s sourced from `Supplier`s with a category and a
concentration profile. Swap the label set — Warehouse → Club location,
Supplier → Vendor, Customer → Member — and every existing DuckDB query and
workflow keeps working, because the shape (id, category, region,
concentration) is domain-agnostic.

## Workflow mapping

Grounded in the four workflows defined in `src/workflows/definitions.py`:

| HVAC workflow (`slug`) | What it computes today | Club-portfolio equivalent |
|---|---|---|
| `refrigerant-exposure` — "Refrigerant exposure analysis" | Dollar exposure to a phase-out refrigerant (R-410A/R-22/etc.), top customers by 24-mo revenue on affected SKUs, regulatory context + retrofit actions | Labor/energy/membership exposure — dollar exposure to a cost driver (minimum-wage law changes, energy contract resets, dues-dependent revenue at risk), top members/segments concentrated in that exposure |
| `tariff-response` — "Tariff / price-change response" | Response plan to a manufacturer price increase: exposure, top exposed customers, pass-through/absorb/hold recommendation against playbook thresholds | Vendor contract risk workflow — response plan to a vendor contract renewal or rate change: exposure, top exposed clubs/categories, renegotiate/absorb/hold recommendation |
| `supplier-risk-review` — "Supplier risk review" | Concentration + substitute coverage for one supplier: trailing spend, category share, flag any category >25% | Vendor concentration — same query shape, applied to F&B/landscaping/maintenance vendors: flag any spend category >25% from one vendor |
| `daily-brief` — "Daily executive brief" | Standing brief: refrigerant exposure, top 3 customers by revenue, supplier concentration >25%, inventory stock-out risk | See `docs/savings-opportunity-tracker.md` — same shape, reframed as a savings-opportunity tracker scored against a $10M target |

## Customer/member concentration

The `refrigerant-exposure` and `daily-brief` workflows already flag
customers concentrated above $50K in 24-month revenue from phase-out SKUs.
The same query — filter on a risk dimension, threshold by revenue, group
by customer — becomes member concentration / churn risk: flag members or
segments with dues-dependent revenue above a threshold, or concentrated in
an at-risk segment. No new tables, no new query pattern — a different
filter value and label.

## Why this isn't a rebuild

Every row above maps an existing field or workflow onto new labels. The
DuckDB schema, the `retrieve` + `run_sql` tool surface, the citation
discipline (`[cN]` sourcing), and the eval baseline are untouched. What
changes for a club-portfolio pitch is vocabulary, not architecture.
