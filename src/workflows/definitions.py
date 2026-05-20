"""Workflow definitions — parameter schemas + prompt templates.

Each ``Workflow`` is enough metadata for:
  - The UI to render a parameter form.
  - The runner to validate input + format a user message for the agent.

Prompts are tuned per workflow to steer the agent toward the right tools
(retrieve for sources, run_sql for numbers, read_wiki_page for synthesis)
and the right output shape (structured H2 sections with citations).

Parameter types accepted by the UI form:
  - ``choice``  — render as <select>; ``choices`` required.
  - ``string``  — render as <input type="text">.
  - ``number``  — render as <input type="number">; ``step`` optional.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

ParamType = Literal["choice", "string", "number"]


@dataclass(frozen=True)
class Parameter:
    name: str
    label: str
    type: ParamType
    choices: list[str] | None = None
    default: Any = None
    required: bool = True
    help: str | None = None
    step: float | None = None  # for number inputs


@dataclass(frozen=True)
class Workflow:
    slug: str
    title: str
    description: str
    parameters: list[Parameter] = field(default_factory=list)
    prompt_template: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "slug": self.slug,
            "title": self.title,
            "description": self.description,
            "parameters": [
                {
                    "name": p.name,
                    "label": p.label,
                    "type": p.type,
                    "choices": p.choices,
                    "default": p.default,
                    "required": p.required,
                    "help": p.help,
                    "step": p.step,
                }
                for p in self.parameters
            ],
        }


REFRIGERANTS = ["R-22", "R-410A", "R-32", "R-454B", "R-1234yf"]

# Supplier and manufacturer choices are NOT hardcoded — workflows take
# free-text input. The system is robust to "Lennox" vs "Lennox PartsPlus"
# because retrieve uses substring matching on the manufacturer column.


REFRIGERANT_EXPOSURE = Workflow(
    slug="refrigerant-exposure",
    title="Refrigerant exposure analysis",
    description=(
        "Pick a refrigerant and get the affected customer list, revenue "
        "exposure, regulatory context, and recommended retrofit actions — "
        "with citations to source documents and SQL queries."
    ),
    parameters=[
        Parameter(
            name="refrigerant",
            label="Refrigerant",
            type="choice",
            choices=REFRIGERANTS,
            default="R-410A",
        ),
        Parameter(
            name="top_n",
            label="Top N customers",
            type="number",
            default=10,
            required=False,
            step=1,
            help="How many top-revenue customers to list (1–25).",
        ),
    ],
    prompt_template="""\
Analyze our exposure to {refrigerant}.

Do this in order:
1. Run a DuckDB query to find the top {top_n} customers by 24-month revenue
   from SKUs where refrigerant = '{refrigerant}'. Include customer name,
   segment, and region.
2. Compute the total 24-month revenue tied to {refrigerant} SKUs.
3. Retrieve regulatory and technical context for {refrigerant}
   (use the retrieve tool with filters={{"refrigerant": "{refrigerant}"}}).
4. Retrieve any internal SOPs about transition/retrofit/pre-buy that apply.
5. If a wiki page exists at refrigerants/{refrigerant_slug}.md, read it.

Produce a structured brief with these H2 sections:

## Exposure summary
Total 24-month revenue tied to {refrigerant}, count of affected customers,
top 1–2 segments.

## Top {top_n} customers
Markdown table: Customer | Segment | Region | 24-mo revenue. Order by revenue.

## Regulatory context
Cite chunks with [cN]. Cover phase-down timeline, replacement options, and
any compliance dates relevant to ops planning.

## Recommended actions
3–5 bulleted recommendations. Cite specific SOPs and bulletins.

Keep the brief under ~600 words. Quote SQL inline in code blocks so the
user can verify the numbers.
""",
)


SUPPLIER_RISK_REVIEW = Workflow(
    slug="supplier-risk-review",
    title="Supplier risk review",
    description=(
        "Review concentration, recent bulletins, and substitute coverage "
        "for a single supplier. Cites recent emails, TSBs, and internal SOPs."
    ),
    parameters=[
        Parameter(
            name="supplier",
            label="Supplier",
            type="string",
            default="Lennox PartsPlus",
            help="Supplier name or partial match (e.g. 'Lennox', 'Carrier').",
        ),
        Parameter(
            name="manufacturer",
            label="Manufacturer focus (optional)",
            type="string",
            required=False,
            default="",
            help="Narrow to one manufacturer (e.g. 'Lennox'). Leave blank for any.",
        ),
    ],
    prompt_template="""\
Review the supplier-risk picture for "{supplier}".

Do this in order:
1. Look up the supplier in DuckDB (suppliers table) and compute trailing
   24-month spend, share of each product category they supply, and any
   single-category share above 25%.
2. Retrieve recent supplier bulletins / emails / allocations mentioning
   "{supplier}" or {manufacturer_filter_clause}.
3. Retrieve internal SOPs about supplier consolidation, bulletin triage,
   or tariff response.
4. Identify whether this supplier carries any category at >25% of our
   total category revenue (concentration risk).

Produce a structured brief with these H2 sections:

## Spend + concentration
Total 24-month spend; per-category share; flag any category >25%.

## Recent signals
Bullet list of recent allocation notices, price changes, or TSBs from this
supplier (or affecting equipment lines they carry). Cite chunks with [cN].

## Substitute coverage
For each category where this supplier is >25% share, identify alternative
suppliers we already buy from (DuckDB). Note whether the substitute coverage
is adequate.

## Risk assessment + recommendations
2–4 short bullets. Cite SOPs.

Under ~600 words. Quote SQL inline.
""",
)


TARIFF_RESPONSE = Workflow(
    slug="tariff-response",
    title="Tariff / price-change response",
    description=(
        "Plan a response to a supplier or manufacturer price change. "
        "Pulls exposure, customer impact, and recommended messaging from "
        "the tariff-response playbook."
    ),
    parameters=[
        Parameter(
            name="manufacturer",
            label="Manufacturer",
            type="string",
            default="Carrier",
            help="Manufacturer that announced the change (e.g. 'Carrier', 'Lennox').",
        ),
        Parameter(
            name="magnitude_pct",
            label="Magnitude (% increase)",
            type="number",
            default=4.2,
            step=0.1,
            help="e.g. 4.2 for a 4.2% increase.",
        ),
        Parameter(
            name="category",
            label="Category (optional)",
            type="string",
            required=False,
            default="",
            help="Narrow to one category (e.g. 'Condenser', 'Motor'). Leave blank for all.",
        ),
    ],
    prompt_template="""\
A supplier announced a {magnitude_pct}% price increase from {manufacturer}
{category_clause}. Plan our response per the tariff-response playbook.

Do this in order:
1. Read the wiki page for the tariff-response playbook if one exists, OR
   retrieve the SOP 'sops/tariff-response-playbook.md' for the procedure.
2. Run the DuckDB query from the playbook to pull 24-month revenue at
   risk for the affected SKUs (manufacturer = '{manufacturer}'{sql_category_clause}).
3. Identify top customers exposed to the change (top 10 by 24-mo revenue
   on the affected SKUs).
4. Retrieve any recent supplier emails from {manufacturer} that confirm
   or contextualize the change.

Produce a structured brief with these H2 sections:

## What changed
One-sentence summary of the change. Cite the supplier-side bulletin/email
if one exists.

## Exposure
Total 24-month revenue at risk; per-SKU share; top exposed customers.

## Pricing decision recommendation
Pass-through, partial absorption, or hold? Reference the playbook's
thresholds (>7%, 3–7%, <3%) explicitly. Cite [cN].

## Customer communication
2–3 bullets on top-25 outreach + bulletin-email content. Cite the
top-customer-pricing-communication SOP if available.

Under ~600 words.
""",
)


DAILY_BRIEF = Workflow(
    slug="daily-brief",
    title="Daily executive brief",
    description=(
        "Run the standing executive brief: refrigerant exposure, top "
        "customers, supplier concentration, inventory health. Same shape "
        "the standalone brief generator produces, now with citations."
    ),
    parameters=[],
    prompt_template="""\
Generate a concise daily operations brief for our HVAC distribution
platform. Write for the business owner / ops lead — signal, not noise.

Cover all four:

1. **Refrigerant exposure** — current dollar exposure to R-410A and R-22
   phase-out; any customers concentrated above $50K in 24-month revenue
   from phase-out SKUs.
2. **Top 3 customers by revenue** — name, segment, region, revenue.
3. **Supplier concentration risk** — any single supplier carrying more
   than 25% of a category's revenue.
4. **Inventory health** — categories at any warehouse with notable
   stock-out risk (units below half the typical reorder point).

For each, use real numbers from DuckDB and cite source documents with
[cN] when you draw on regulatory / SOP context. Keep under 500 words.
Use markdown headings and bullet points.
""",
)


WORKFLOWS: list[Workflow] = [
    REFRIGERANT_EXPOSURE,
    SUPPLIER_RISK_REVIEW,
    TARIFF_RESPONSE,
    DAILY_BRIEF,
]


def get_workflow(slug: str) -> Workflow | None:
    for w in WORKFLOWS:
        if w.slug == slug:
            return w
    return None
