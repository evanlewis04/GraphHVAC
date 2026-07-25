# Savings Opportunity Tracker — a positioning reframe of the Daily Brief

**This is a reframe of an existing, working pattern, not a new build.**
No changes to `src/briefs/generator.py`, the agent loop, the citation
discipline, or the eval baseline. See `docs/MAPPING.md` for the underlying
entity/workflow translation this reframe draws on.

## What it is today

`src/briefs/generator.py::generate_brief()` runs the full agent loop
(`run_agent`) against a fixed prompt (`DAILY_BRIEF_PROMPT`) and writes the
dated result to `data/briefs/YYYY-MM-DD.md` — the same audit trail, same
tool surface, same trust model as every other workflow in the app. The
module docstring already calls this "the leave-behind artifact for PE
operating partners — what would land in their inbox at 7am." That framing
is not a stretch for Invited; it's their ask as stated.

The current prompt covers four fixed sections, each grounded in real
DuckDB numbers and cited with `[cN]` where it draws on regulatory/SOP
context:

1. **Refrigerant exposure** — current dollar exposure to R-410A/R-22
   phase-out; customers concentrated above $50K in 24-month revenue from
   phase-out SKUs.
2. **Top 3 customers by revenue** — name, segment, region, revenue.
3. **Supplier concentration risk** — any single supplier carrying more
   than 25% of a category's revenue.
4. **Inventory health** — categories at any warehouse with notable
   stock-out risk (units below half the typical reorder point).

Same shape every time: agent loop → cited answer → dated markdown file →
rendered in the Daily Brief tab. Nothing about that shape is HVAC-specific.

## What changes for Invited

Same structure, same trust model, one addition: each opportunity is scored
against a running savings target instead of reported open-ended. Using the
translations from `docs/MAPPING.md`:

1. **Labor/energy/membership exposure** — dollar exposure to a cost
   driver (minimum-wage changes, energy contract resets, dues-dependent
   revenue at risk), same query shape as refrigerant exposure today.
2. **Top concentrated members/segments** — same "top N by revenue"
   pattern, applied to member/segment concentration instead of customer
   revenue.
3. **Vendor concentration risk** — any single vendor (F&B, landscaping,
   maintenance) carrying more than 25% of a spend category, same query
   as supplier concentration today.
4. **Opportunity log, scored against the $10M target** — instead of open
   inventory-health reporting, each cited finding becomes a line item with
   a dollar estimate and running progress, e.g.:

   > **Opportunity:** renegotiate landscaping vendor X — $340K/yr
   > (vendor carries 38% of the landscaping category spend across 4
   > clubs) [c3]. Cumulative progress: $2.1M / $10M target.

## Why this is the right leave-behind, not a new build

The tracker is the daily brief with a running total bolted onto the
existing "cited findings" output — no new tools, no new query pattern, no
new trust model. The citation discipline and eval numbers (recall,
cost-per-query) that already back the HVAC brief carry over unchanged;
what's new is a target and a cumulative-progress line, which is a
formatting decision, not an architecture change.
