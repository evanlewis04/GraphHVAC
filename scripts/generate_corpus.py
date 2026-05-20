"""Generate the synthetic source corpus for Phase 2.

Produces deliberately-messy bulk content (manufacturer TSBs, supplier
emails, internal SOPs, service tickets, spec CSVs) on top of the
hand-authored showcase fixtures already under data/sources/.

Deterministic — seeded via ``--seed`` (default 7).

Final step builds ``data/sources/manifest.yaml`` by:
  1. Scanning every file under data/sources/ (excluding manifest.yaml
     and README.md).
  2. For markdown files, harvesting frontmatter as the manifest entry.
  3. For files without frontmatter (csv, jsonl), reading a sidecar
     ``<filename>.meta.yaml`` if present, otherwise inferring metadata
     from the bucket directory and file name.
  4. Appending entries for real anchors declared in REAL_ANCHORS (these
     are reference-only; files may not exist on disk until
     ``fetch_anchors.py`` is run).

Usage:
    python scripts/generate_corpus.py
    python scripts/generate_corpus.py --seed 42 --quiet
    python scripts/generate_corpus.py --manifest-only   # skip generation
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import re
import textwrap
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import yaml

SOURCES_DIR = Path(__file__).resolve().parents[1] / "data" / "sources"

# ---------------------------------------------------------------------------
# Domain vocabulary (intentionally overlaps with src/ingest/synthetic.py).
# Kept in sync by hand for now; will fold into a shared module in Phase 3
# if duplication becomes an issue.
# ---------------------------------------------------------------------------

MANUFACTURERS = [
    "Lennox", "Carrier", "Trane", "Goodman", "Rheem", "York", "Daikin",
    "Mitsubishi", "Bryant", "Heil", "Amana", "Honeywell",
]

SUPPLIERS = [
    "Lennox PartsPlus", "Carrier Enterprise", "Trane Supply", "Johnstone Supply",
    "RE Michel", "Gemaire Distributors", "Baker Distributing", "Munch's Supply",
    "Goodin Company", "ABCO Distribution", "Coastal HVAC Supply",
    "Northern HVAC Wholesale",
]

REFRIGERANTS = ["R-410A", "R-32", "R-454B", "R-22", "R-1234yf"]

CATEGORIES = [
    ("Capacitor", ["Run", "Start", "Dual-Run", "Hard-Start"]),
    ("Contactor", ["1-Pole", "2-Pole", "3-Pole"]),
    ("Motor", ["Condenser Fan", "Blower", "ECM Blower", "Inducer"]),
    ("Coil", ["Evaporator", "Condenser", "A-Coil", "Slab"]),
    ("ControlBoard", ["Furnace IFC", "Ignition Module", "Defrost Board"]),
    ("Thermostat", ["Programmable", "Smart Wi-Fi", "Conventional", "Heat-Pump"]),
]

REGIONS = ["Southeast", "Southwest", "Midwest", "Northeast", "West"]
WAREHOUSES = ["WH-ATL", "WH-DAL", "WH-PHX", "WH-CHI", "WH-CHA"]

# ---------------------------------------------------------------------------
# Real public anchors. Listed in the manifest with license: reference-only;
# files are NOT in the repo. scripts/fetch_anchors.py downloads them on demand.
# ---------------------------------------------------------------------------

HAND_AUTHORED: dict[str, set[str]] = {
    "bulletins": {
        "epa-aim-act-summary.md",
        "r-410a-phase-out-timeline.md",
        "r-32-transition-overview.md",
        "r-454b-overview.md",
        "mfr-lennox-tsb-2024-001-icomfort.md",
        "mfr-carrier-tsb-2024-007-fan-motor.md",
        "mfr-trane-tsb-2024-002-r-32-launch.md",
    },
    "sops": {
        "tariff-response-playbook.md",
        "r-410a-retrofit-customer-outreach.md",
        "warranty-claim-escalation.md",
        "supplier-consolidation-post-mna.md",
        "refrigerant-pre-buy-guidance.md",
        "supplier-bulletin-triage.md",
    },
    "emails": {
        "lennox-2025-q1-allocations.md",
        "carrier-tariff-passthrough-2025-03.md",
    },
    "manuals": {
        "synth-install-residential-condenser.md",
    },
    "tickets": set(),
    "specs": set(),
}


def _wipe_generated(bucket_dir: Path, keep: set[str]) -> int:
    """Delete every file in bucket_dir that isn't in keep (or .gitkeep)."""
    if not bucket_dir.exists():
        return 0
    n = 0
    for p in bucket_dir.iterdir():
        if not p.is_file():
            continue
        if p.name == ".gitkeep":
            continue
        if p.name in keep:
            continue
        # sidecars follow the file they describe; deleted-with-data
        p.unlink()
        n += 1
    return n


REAL_ANCHORS: list[dict[str, Any]] = [
    {
        "source_id": "anchor-epa-aim-act-final-rule",
        "path": "bulletins/anchor-epa-aim-act-final-rule.pdf",
        "type": "pdf",
        "bucket": "bulletins",
        "title": "EPA AIM Act Final Rule on HFC Phase-down",
        "issuer": "EPA",
        "refrigerants": ["R-410A", "R-22", "R-32", "R-454B"],
        "regulations": ["AIM-Act"],
        "license": "reference-only",
        "fetch": "https://www.epa.gov/system/files/documents/2021-09/aim-act-final-rule.pdf",
    },
    {
        "source_id": "anchor-epa-snap-rule-23-summary",
        "path": "bulletins/anchor-epa-snap-rule-23-summary.pdf",
        "type": "pdf",
        "bucket": "bulletins",
        "title": "EPA SNAP Rule 23 (Refrigerant Alternatives)",
        "issuer": "EPA",
        "refrigerants": ["R-410A", "R-32", "R-454B"],
        "regulations": ["EPA-SNAP"],
        "license": "reference-only",
        "fetch": "https://www.epa.gov/snap/snap-final-rule-23",
    },
    {
        "source_id": "anchor-doe-residential-cac-rule",
        "path": "bulletins/anchor-doe-residential-cac-rule.pdf",
        "type": "pdf",
        "bucket": "bulletins",
        "title": "DOE Energy Conservation Standards — Residential Central AC",
        "issuer": "DOE",
        "license": "reference-only",
        "fetch": "https://www.energy.gov/eere/buildings/articles/residential-central-air-conditioners-and-heat-pumps",
    },
]


# ---------------------------------------------------------------------------
# Generators
# ---------------------------------------------------------------------------


def _slugify(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def _frontmatter(meta: dict[str, Any]) -> str:
    """Render a YAML frontmatter block from a dict."""
    lines = ["---"]
    for k, v in meta.items():
        if isinstance(v, list):
            lines.append(f"{k}: [{', '.join(str(x) for x in v)}]")
        else:
            lines.append(f"{k}: {v}")
    lines.append("---\n")
    return "\n".join(lines)


# ----- TSBs (generated bulletins) ------------------------------------------

TSB_TEMPLATES = [
    ("control-board-replacement",
     "Control board replacement procedure — {model} series",
     "Subject: {model} furnace IFC control board (P/N {pn}) replacement procedure.",
     "Symptom: intermittent ignition failure; status LED shows flash code 3 (pressure switch). "
     "Confirmed not to be a pressure switch failure — control board MOSFET drift on extended cycles.",
     "Resolution: replace IFC board with {pn}. Procedure: shut off gas, kill power, label all "
     "low-voltage leads at the board, swap board, verify dip-switch positions match the old "
     "board exactly, restore power, verify ignition through three cycles.",
     "Warranty: standard 5-year parts."),
    ("ecm-blower-firmware",
     "ECM blower module firmware update — {model}",
     "Subject: ECM blower module on {model} platform — firmware update for low-airflow alarm.",
     "Symptom: ECM blower posts low-airflow alarm code 21 on standard 0.5 in. WC static. "
     "Customers report unit running but reduced airflow at the registers.",
     "Resolution: Apply firmware update {pn} via the OEM service tool (kit ST-FW-200). "
     "Update preserves dip-switch configuration. Estimated 8 minutes per unit.",
     "Warranty: not warranty-replacement-eligible; firmware-only fix."),
    ("capacitor-batch-recall",
     "Capacitor batch — voluntary replacement program",
     "Subject: 35 MFD / 440V dual-run capacitor — voluntary replacement of batch {pn}.",
     "Symptom: a subset of capacitors from production batch {pn} were measured at 8–12% under "
     "rated capacitance out of bag. Symptom in the field is hard-start on the compressor and "
     "compressor short-cycling.",
     "Resolution: replace any in-stock units from the affected batch. Free replacement program "
     "open through end-of-quarter. Old units returned per standard RA process; do not discard.",
     "Warranty: full credit for any installed unit failing within 90 days; standard 1-year on "
     "all replacements."),
    ("inducer-motor-bearing",
     "Inducer motor — bearing wear pattern",
     "Subject: inducer motor on {model} — bearing wear after extended cycle counts.",
     "Symptom: inducer motor audible bearing growl, progressing over 2-3 months, eventual "
     "lock-up. Affects units operating in dirty environments (commercial kitchens, agricultural).",
     "Resolution: replace with sealed-bearing variant {pn}. Customer is responsible for adding "
     "filtration if the install environment is dirty.",
     "Warranty: standard 5-year parts."),
    ("thermostat-wifi-reconnect",
     "Smart thermostat — Wi-Fi auto-reconnect behavior",
     "Subject: {model} smart thermostat — Wi-Fi auto-reconnect on router reboot.",
     "Symptom: after a router restart or ISP-side network reset, thermostat does not auto-"
     "reconnect to Wi-Fi. HVAC control continues to function locally; remote app does not.",
     "Resolution: firmware update {pn}. OTA delivery to thermostats with active cloud "
     "connectivity; manual USB update for thermostats that have lost connectivity.",
     "Warranty: not warranty-replacement eligible; software-only fix."),
]


def gen_tsbs(rng: random.Random, out_dir: Path) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    # Generate 13 TSBs across manufacturers; cycle through templates.
    for i in range(1, 14):
        mfr = MANUFACTURERS[i % len(MANUFACTURERS)]
        if mfr in ("Lennox", "Carrier", "Trane"):
            # we already hand-authored a TSB for these — skip
            mfr = MANUFACTURERS[(i + 3) % len(MANUFACTURERS)]
        tmpl = TSB_TEMPLATES[i % len(TSB_TEMPLATES)]
        slug, title_t, *paras = tmpl
        model = f"{mfr[:3].upper()}{rng.randint(100, 999)}"
        pn = f"{mfr[:2].upper()}-{rng.randint(10000, 99999)}"
        doc_date = date(2024, 1, 1) + timedelta(days=rng.randint(0, 330))
        seq = f"{i:03d}"

        fname = f"mfr-{_slugify(mfr)}-tsb-2024-{seq}-{slug}.md"
        meta = {
            "source_id": f"bulletin-{_slugify(mfr)}-tsb-2024-{seq}-{slug}",
            "type": "markdown",
            "bucket": "bulletins",
            "title": f"{mfr} TSB 2024-{seq} — " + title_t.format(model=model),
            "issuer": f"{mfr} (synthetic)",
            "manufacturer": mfr,
            "doc_date": doc_date.isoformat(),
            "license": "synthetic-internal",
        }
        body_paras = [p.format(model=model, pn=pn) for p in paras]
        content = _frontmatter(meta) + "\n# {mfr} Technical Service Bulletin 2024-{seq}\n\n".format(
            mfr=mfr, seq=seq
        )
        content += "\n\n".join(body_paras) + "\n"
        path = out_dir / fname
        path.write_text(content, encoding="utf-8")
        paths.append(path)
    return paths


# ----- Generated SOPs ------------------------------------------------------

SOP_TEMPLATES = [
    ("inventory-reorder-policy",
     "Inventory reorder policy",
     ["Reorder is triggered when on-hand quantity drops below the reorder point set per SKU.",
      "Reorder points are recalculated quarterly based on the trailing 26 weeks of demand and a "
      "safety stock factor of 1.5× weekly demand for the cooling-season SKUs (May–Aug) and 1.2× "
      "for off-season SKUs.",
      "Long-lead suppliers (ocean freight, > 6 weeks) carry a manual override per category set "
      "by purchasing.",
      "Counter staff cannot bypass reorder points without VP Ops approval; emergency stock-out "
      "events are logged in the inventory exception log."]),
    ("credit-hold-procedure",
     "Credit hold procedure",
     ["Customer accounts move to credit hold when (a) any invoice ages > 60 days, (b) total "
      "AR exceeds approved credit limit, or (c) NSF/check-return event within 12 months.",
      "Credit hold blocks new orders at the counter and through online ordering.",
      "Sales rep is notified the same day. Customer must clear the trigger to come off hold; "
      "VP Sales can grant a 7-day grace window for top-50 customers (24-mo revenue rank).",
      "Recurring offenders (3 holds in 12 months) require a deposit at order placement."]),
    ("price-book-update-procedure",
     "Price book update procedure",
     ["Quarterly price book refresh is the primary cadence. Off-cycle updates triggered by "
      "supplier price changes follow the tariff playbook (see sops/tariff-response-playbook).",
      "Mechanics: pull updated supplier costs into the staging table, apply category margin "
      "policy, generate the proposed price book, review with sales and pricing committee, "
      "publish to the ERP and the counter terminals.",
      "Audit: every off-cycle update is logged with the supplier bulletin source, the SKUs "
      "affected, and the date of effect.",
      "Customer comms: top-25 customers by 24-mo revenue receive direct rep contact; remainder "
      "receive the bulletin email."]),
    ("counter-day-runbook",
     "Counter day runbook",
     ["Counter opens 7am, closes 5pm at all warehouses except Phoenix (6am open).",
      "Pre-open: counter staff confirms cash drawer, prints day's open POs, verifies high-"
      "demand SKU on-hand against the morning replenishment.",
      "Standard transactions: cash sale, account sale (charge to customer account), pickup of "
      "online order, warranty swap, return.",
      "Edge cases: refrigerant sale (record EPA 608 cert # on receipt), credit-hold customer "
      "(direct to billing), refused delivery (return to receiving), allocated SKU "
      "(see allocation log before promising delivery)."]),
    ("emergency-stock-allocation",
     "Emergency stock allocation between warehouses",
     ["Inter-warehouse transfers are used to address regional stock-out. Transfer is initiated "
      "by warehouse manager request to purchasing.",
      "Approval is automatic for SKUs with < 4 days of regional stock. Above that threshold, "
      "VP Ops approval required.",
      "Transfer cost is allocated 50/50 between origin and destination warehouses for the "
      "current period.",
      "Receiving warehouse must confirm receipt within 48h or the transfer auto-reverses."]),
    ("backorder-communication",
     "Backorder communication SLA",
     ["Backorder occurs when an order line item ships partial or short. Customer is notified "
      "within 4 business hours of the shipment leaving.",
      "Backorder ETA is updated every 5 business days until the SKU ships. If ETA slips beyond "
      "10 business days, the line item is offered for substitute or cancellation.",
      "Substitutes are sourced per the wiki SKU substitute table; if no listed substitute, "
      "purchasing identifies an OEM-cross alternative.",
      "Customer service tracks backorder cycle time as a KPI; weekly report to VP Ops."]),
    ("return-and-rma-policy",
     "Return and RMA policy",
     ["Counter returns within 30 days, original receipt, original packaging — full credit.",
      "Counter returns 30–60 days — restocking fee (15%) at counter manager discretion.",
      "Beyond 60 days — case-by-case; default deny.",
      "Refrigerant returns are not accepted under any circumstance unless an unopened cylinder "
      "from a clearly damaged shipment is returned within 14 days of delivery.",
      "Special-order SKUs (non-stock, brought in for a specific job) are non-returnable except "
      "for warranty defect."]),
    ("new-customer-onboarding",
     "New customer onboarding",
     ["New contractor customer signs the account application; provides EIN, certificate of "
      "insurance, EPA 608 certification (or specifies they will buy through a certified tech).",
      "Credit application: trade references (3), bank reference, requested credit limit.",
      "Approval flow: standard for credit < $25K; CFO sign-off for > $25K.",
      "Onboarding session: counter walkthrough, online portal demo, account rep introduction, "
      "first-order discount code.",
      "Tag customer in CRM with segment (residential / commercial / property mgr / builder) "
      "and region. Drives reporting in the daily exec brief."]),
    ("top-customer-pricing-communication",
     "Top customer pricing communication template",
     ["Triggered by any pricing change affecting a top-25 customer's commonly-purchased SKUs.",
      "Channel: direct call from account rep, followed by an email confirming the conversation.",
      "Content: effective date, magnitude, the substitute path if one exists, an offer for a "
      "pre-buy at the old price if the customer has unfulfilled commitments.",
      "Cadence: same-day for tariff and allocation-driven changes; within 3 days for routine "
      "supplier price changes.",
      "Log every conversation in CRM with timestamp and customer reaction."]),
    ("customer-concentration-review",
     "Customer concentration review",
     ["Quarterly review of customer revenue concentration by VP Sales + CFO.",
      "Metrics: top-10 share of TTM revenue, top-25 share, single-customer maximum share.",
      "Risk thresholds: top-10 > 35% or single customer > 7% triggers an action plan.",
      "Action plans: targeted outreach to mid-tier customers to grow their share, evaluation "
      "of segment exposure (e.g. heavy concentration in property managers), and contract terms "
      "review on the largest accounts."]),
    ("supplier-rebate-tracking",
     "Supplier rebate tracking",
     ["Each supplier rebate program enrolled is recorded with: tier thresholds, accrual basis, "
      "payment cadence, program start and end dates, and our YTD volume against tier.",
      "Monthly: AR-side rebate accrual is recorded as a contra-COGS entry per program.",
      "Quarterly: reconcile booked accrual against the supplier's published statement. Disputes "
      "flagged to the supplier within 30 days; otherwise considered accepted.",
      "Year-end: confirm program tier achievement and book any retroactive adjustments."]),
    ("seasonal-stocking-plan",
     "Seasonal stocking plan",
     ["Pre-cooling-season (Mar–Apr) stocking targets: 10 weeks of cooling-side SKU demand "
      "(capacitors, contactors, condenser fans, R-410A and R-454B refrigerant).",
      "Pre-heating-season (Sep–Oct) stocking targets: 8 weeks of heating-side SKU demand "
      "(igniters, gas valves, inducer motors, furnace IFC boards).",
      "Stocking levels are set at the per-warehouse level using a regional demand model.",
      "Override: warehouse manager can request +/- 15% from purchasing without VP Ops approval "
      "if local conditions warrant (e.g. early heat wave forecast)."]),
]


def gen_sops(rng: random.Random, out_dir: Path) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for slug, title, paras in SOP_TEMPLATES:
        meta = {
            "source_id": f"sop-{slug}",
            "type": "markdown",
            "bucket": "sops",
            "title": title,
            "issuer": "Internal Ops",
            "doc_date": (date(2023, 6, 1) + timedelta(days=rng.randint(0, 700))).isoformat(),
            "license": "synthetic-internal",
        }
        content = _frontmatter(meta) + f"\n# {title}\n\n"
        content += "Owner: Operations. Internal SOP.\n\n"
        for i, p in enumerate(paras, 1):
            content += f"## Section {i}\n\n{p}\n\n"
        path = out_dir / f"{slug}.md"
        path.write_text(content, encoding="utf-8")
        paths.append(path)
    return paths


# ----- Generated supplier emails -------------------------------------------

EMAIL_TOPICS = [
    ("price-increase", "Q{q} price adjustment — {category} line",
     "We're writing to confirm a {pct}% list price adjustment on the {category} line, effective "
     "{effective_date}. The change reflects raw material cost pressure (copper, aluminum) and "
     "minor refrigerant component cost. Updated price book ships {pricebook_date}."),
    ("allocation-notice", "Q{q} allocation update — {category}",
     "Our {category} capacity for Q{q} is allocated at {pct}% of trailing-quarter volume across "
     "the channel. Your account allocation specifically: see attached. We expect easing in Q{nextq} "
     "as the {plant} line ramps."),
    ("product-discontinuation", "End-of-life notice — {model} series",
     "The {model} series will reach end-of-production on {effective_date}. Terminal inventory "
     "will be allocated to active orders only; no new POs against {model} accepted after "
     "{cutoff_date}. Replacement model {replacement} is now in standard production."),
    ("delivery-delay", "Shipment delay notice — {category}",
     "We're seeing a {weeks}-week delay on {category} shipments out of the {plant} facility due "
     "to a freight carrier issue. Your in-flight POs will be re-scheduled and you'll receive an "
     "updated ETA by {update_date}."),
    ("rebate-program", "2025 {program} rebate program — enrollment open",
     "Enrollment is now open for the 2025 {program} program. Tier thresholds, accrual basis, and "
     "program-year boundaries are unchanged from 2024. Submit your enrollment confirmation by "
     "{enrollment_deadline}."),
]

SUPPLIER_REP_NAMES = [
    "Marcus Hale", "Diane Yu", "Sarah Patel", "Carlos Romero", "Beth Nguyen",
    "Greg Ostrowski", "Jamie Carrillo", "Pat Reyes", "Anders Kim", "Lin Park",
]

INTERNAL_BUYER_NAMES = ["Jenna Reed", "Tom Brennan", "Rita Velasquez"]


def gen_emails(rng: random.Random, out_dir: Path) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    # 30 generated emails on top of the 2 hand-authored ones.
    for i in range(30):
        topic = rng.choice(EMAIL_TOPICS)
        slug, subj_t, body_t = topic
        mfr = rng.choice(MANUFACTURERS)
        supplier = rng.choice(SUPPLIERS)
        category, sub_types = rng.choice(CATEGORIES)
        rep_name = rng.choice(SUPPLIER_REP_NAMES)
        rep_email = (
            rep_name.lower().replace(" ", ".")
            + "@" + supplier.lower().replace(" ", "").replace("'", "")
            + ".example"
        )
        internal_name = rng.choice(INTERNAL_BUYER_NAMES)
        doc_date = date(2024, 1, 1) + timedelta(days=rng.randint(0, 500))

        params = {
            "q": rng.choice([1, 2, 3, 4]),
            "nextq": rng.choice([1, 2, 3, 4]),
            "category": category,
            "pct": rng.randint(2, 12),
            "effective_date": (doc_date + timedelta(days=rng.randint(14, 60))).isoformat(),
            "pricebook_date": (doc_date + timedelta(days=rng.randint(7, 30))).isoformat(),
            "cutoff_date": (doc_date + timedelta(days=rng.randint(30, 90))).isoformat(),
            "update_date": (doc_date + timedelta(days=rng.randint(5, 14))).isoformat(),
            "enrollment_deadline": (doc_date + timedelta(days=30)).isoformat(),
            "model": f"{mfr[:3].upper()}{rng.randint(100, 999)}",
            "replacement": f"{mfr[:3].upper()}{rng.randint(100, 999)}",
            "plant": rng.choice(["Stuttgart", "Tianjin", "Mexicali", "Charlotte", "Tipton"]),
            "weeks": rng.choice([2, 3, 4, 6]),
            "program": rng.choice(["Volume Plus", "Partner Tier", "Master Rebate", "Loyalty"]),
        }
        subject = subj_t.format(**params)
        body = body_t.format(**params)

        seq = f"{i:03d}"
        fname = f"{_slugify(supplier)}-{doc_date.isoformat()}-{slug}-{seq}.md"
        meta = {
            "source_id": f"email-{_slugify(supplier)}-{doc_date.isoformat()}-{slug}-{seq}",
            "type": "email",
            "bucket": "emails",
            "title": f"{supplier} — {subject}",
            "issuer": supplier,
            "manufacturer": mfr,
            "doc_date": doc_date.isoformat(),
            "license": "synthetic-internal",
        }
        content = _frontmatter(meta) + "\n# " + supplier + " — " + subject + "\n\n"
        content += "---\n\n"
        content += f"**From:** {rep_name} <{rep_email}>\n"
        content += "**To:** purchasing@graph-distributor.example\n"
        content += f"**Date:** {doc_date.isoformat()} 10:{rng.randint(10,59):02d} EST\n"
        content += f"**Subject:** {subject}\n\n"
        content += body + "\n\n"
        content += f"Thanks,\n{rep_name}\n{supplier}\n\n---\n\n"
        # Sometimes append a brief internal reply for realism
        if rng.random() < 0.45:
            reply_date = doc_date + timedelta(days=rng.randint(1, 3))
            content += "**From:** purchasing@graph-distributor.example\n"
            content += f"**To:** {rep_name} <{rep_email}>\n"
            content += f"**Date:** {reply_date.isoformat()} 14:{rng.randint(10,59):02d} EST\n"
            content += f"**Subject:** Re: {subject}\n\n"
            content += rng.choice([
                "Acknowledged. We'll process accordingly and update our records.\n",
                f"Thanks {rep_name.split()[0]}. Couple of questions — can you confirm the SKUs "
                "affected? We have customer comms going out and want to be precise.\n",
                "Got it. Will incorporate into the next price-book cycle. Any visibility into "
                "Q3 / Q4 from here?\n",
            ])
            content += f"\n— {internal_name}\nGraph Distributor | Purchasing\n"
        path = out_dir / fname
        path.write_text(content, encoding="utf-8")
        paths.append(path)
    return paths


# ----- Generated service tickets -------------------------------------------

TICKET_FAULT_PATTERNS = [
    "compressor short-cycling, suspect run cap",
    "no heat, ignitor flashing 3x — likely IFC board",
    "low refrigerant — leak at flare on liquid line",
    "blower not starting, ECM module fault code 21",
    "condenser fan locked rotor — bearing growl history",
    "thermostat lost wifi after power outage",
    "drain pan overflow — float switch tripped",
    "high head pressure — dirty condenser coil",
    "intermittent humming at contactor pull-in",
    "evap freezing up — low airflow, restricted filter",
]

TICKET_QUESTIONS = [
    "need substitute for {pn} — backordered 6 weeks",
    "is {pn} compatible with {model}?",
    "warranty status on {pn} purchased {months}m ago",
    "any cross-ref on {pn} from a non-OEM supplier?",
    "do you have 25-lb R-454B cylinders in stock at {wh}?",
    "training kit for A2L service — what's in it?",
    "R-410A pre-buy quote for 50 cylinders, picked up at {wh}",
    "credit hold? trying to place order #{po}",
]


def gen_tickets(rng: random.Random, out_dir: Path) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    # Four JSONL files, each covering a quarter.
    quarters = [
        ("contractor-notes-2024-q3", date(2024, 7, 1), date(2024, 9, 30)),
        ("contractor-notes-2024-q4", date(2024, 10, 1), date(2024, 12, 31)),
        ("counter-day-2025-q1", date(2025, 1, 1), date(2025, 3, 31)),
        ("warranty-claims-2024", date(2024, 1, 15), date(2024, 12, 20)),
    ]
    for slug, start, end in quarters:
        days_span = (end - start).days
        records: list[dict[str, Any]] = []
        n = rng.randint(9, 12)
        for i in range(n):
            ticket_id = f"TKT-{slug[-7:].upper()}-{i+1:03d}"
            d = start + timedelta(days=rng.randint(0, days_span))
            customer_id = f"CUS-{rng.randint(1, 500):04d}"
            mfr = rng.choice(MANUFACTURERS)
            model = f"{mfr[:3].upper()}{rng.randint(100,999)}"
            pn = f"{mfr[:2].upper()}-{rng.randint(10000, 99999)}"
            wh = rng.choice(WAREHOUSES)
            if "warranty" in slug:
                fault = rng.choice(TICKET_FAULT_PATTERNS)
                notes_pool = [
                    f"Tech: {fault}. Confirmed in field. Need warranty swap of {pn}.",
                    f"Contractor reports {fault}. Photos attached. Cert # 608-{rng.randint(1000,9999)}.",
                    f"{fault}. Within warranty? Bought {rng.randint(3,40)} months ago.",
                ]
            else:
                q_t = rng.choice(TICKET_QUESTIONS)
                q = q_t.format(
                    pn=pn,
                    model=model,
                    months=rng.randint(2, 30),
                    wh=wh,
                    po=f"{rng.randint(40000, 99999)}",
                )
                notes_pool = [
                    q,
                    f"customer asked: {q}",
                    f"counter call — {q}. Followed up by email.",
                ]
            record = {
                "ticket_id": ticket_id,
                "date": d.isoformat(),
                "customer_id": customer_id,
                "equipment_model": model,
                "manufacturer": mfr,
                "warehouse": wh,
                "notes": rng.choice(notes_pool),
            }
            if "warranty" in slug:
                record["fault_code"] = rng.choice(["E21", "E33", "F-04", "P-LOW", "LOCK"])
                record["parts_used"] = pn
            records.append(record)

        path = out_dir / f"{slug}.jsonl"
        with path.open("w", encoding="utf-8") as f:
            for r in records:
                f.write(json.dumps(r) + "\n")
        paths.append(path)

        # Sidecar .meta.yaml describing the file for the manifest builder.
        meta_path = path.with_suffix(".jsonl.meta.yaml")
        meta = {
            "source_id": f"ticket-{slug}",
            "type": "ticket",
            "bucket": "tickets",
            "title": slug.replace("-", " ").title(),
            "issuer": "Internal",
            "doc_date": end.isoformat(),
            "record_count": len(records),
            "license": "synthetic-internal",
        }
        meta_path.write_text(yaml.safe_dump(meta, sort_keys=False), encoding="utf-8")
    return paths


# ----- Generated spec CSVs -------------------------------------------------

def gen_specs(rng: random.Random, out_dir: Path) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    spec_sets = [
        ("lennox-2025-condenser-pricebook-excerpt",
         "Lennox", "Condenser", ["model", "tonnage", "refrigerant", "list_price", "tier_2_price"]),
        ("carrier-2025-residential-condensers",
         "Carrier", "Condenser", ["model", "tonnage", "refrigerant", "list_price", "tier_2_price"]),
        ("trane-2024-commercial-r-32",
         "Trane", "Condenser", ["model", "tonnage", "refrigerant", "list_price", "tier_2_price"]),
        ("goodman-2024-furnace-ifc-boards",
         "Goodman", "ControlBoard", ["part_no", "model_fit", "list_price", "tier_2_price"]),
        ("rheem-2025-r-454b-condensers",
         "Rheem", "Condenser", ["model", "tonnage", "refrigerant", "list_price", "tier_2_price"]),
        ("johnstone-2025-q1-capacitors",
         "Mixed", "Capacitor", ["part_no", "mfd", "voltage", "list_price"]),
        ("re-michel-2025-q1-contactors",
         "Mixed", "Contactor", ["part_no", "poles", "amp_rating", "list_price"]),
        ("baker-2025-blower-motors",
         "US Motors", "Motor", ["part_no", "hp", "voltage", "list_price"]),
    ]
    for slug, mfr, category, cols in spec_sets:
        path = out_dir / f"{slug}.csv"
        with path.open("w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(cols)
            rows = rng.randint(15, 35)
            for _ in range(rows):
                if "model" in cols:
                    row = [
                        f"{mfr[:3].upper()}{rng.randint(100,999)}",
                        f"{rng.choice([1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 5.0]):.1f}",
                        rng.choice(["R-410A", "R-32", "R-454B"]),
                        f"{rng.randint(2200, 6800)}.00",
                        f"{rng.randint(1900, 6000)}.00",
                    ]
                elif category == "ControlBoard":
                    row = [
                        f"GD-{rng.randint(10000,99999)}",
                        f"{rng.choice(['GMS','GMV','GME'])}{rng.randint(60,120)}",
                        f"{rng.randint(140,290)}.00",
                        f"{rng.randint(110,240)}.00",
                    ]
                elif category == "Capacitor":
                    row = [
                        f"CAP-{rng.choice(MANUFACTURERS)[:3].upper()}-{rng.randint(1000,9999)}",
                        f"{rng.choice([5, 7.5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55])}",
                        rng.choice([370, 440]),
                        f"{rng.randint(8, 45)}.{rng.randint(0,99):02d}",
                    ]
                elif category == "Contactor":
                    row = [
                        f"CON-{rng.choice(MANUFACTURERS)[:3].upper()}-{rng.randint(1000,9999)}",
                        rng.choice([1, 2, 3]),
                        rng.choice([20, 25, 30, 40]),
                        f"{rng.randint(12, 65)}.{rng.randint(0,99):02d}",
                    ]
                else:  # Motor
                    row = [
                        f"MTR-USM-{rng.randint(1000,9999)}",
                        rng.choice([0.25, 0.33, 0.5, 0.75, 1.0]),
                        rng.choice([115, 208, 230]),
                        f"{rng.randint(80, 320)}.00",
                    ]
                w.writerow(row)
        paths.append(path)

        meta_path = path.with_suffix(".csv.meta.yaml")
        meta = {
            "source_id": f"spec-{slug}",
            "type": "csv",
            "bucket": "specs",
            "title": slug.replace("-", " ").title(),
            "issuer": mfr if mfr != "Mixed" else "Distributor",
            "manufacturer": mfr if mfr != "Mixed" else None,
            "category": category,
            "doc_date": date(2024 + (1 if "2025" in slug else 0), 1, 15).isoformat(),
            "license": "synthetic-internal",
        }
        # strip None values
        meta = {k: v for k, v in meta.items() if v is not None}
        meta_path.write_text(yaml.safe_dump(meta, sort_keys=False), encoding="utf-8")
    return paths


# ---------------------------------------------------------------------------
# Manifest builder
# ---------------------------------------------------------------------------


FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


def _parse_frontmatter(text: str) -> dict[str, Any] | None:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return None
    return yaml.safe_load(m.group(1))


def build_manifest() -> dict[str, Any]:
    """Walk data/sources/, harvest frontmatter and sidecars, assemble manifest."""
    entries: list[dict[str, Any]] = []
    seen_ids: set[str] = set()

    # Walk every file under data/sources/ except the manifest itself, README,
    # and any sidecar .meta.yaml (those describe other files).
    for path in sorted(SOURCES_DIR.rglob("*")):
        if not path.is_file():
            continue
        if path.name in ("manifest.yaml", "README.md"):
            continue
        if path.name == ".gitkeep":
            continue
        if path.name.endswith(".meta.yaml"):
            continue

        rel = path.relative_to(SOURCES_DIR).as_posix()

        if path.suffix == ".md":
            text = path.read_text(encoding="utf-8")
            fm = _parse_frontmatter(text)
            if fm is None or "source_id" not in fm:
                continue  # skip un-manifested markdown (shouldn't happen)
            entry = {
                "source_id": fm["source_id"],
                "path": rel,
                "type": fm.get("type", "markdown"),
                "bucket": fm.get("bucket", path.parent.name),
                "title": fm.get("title"),
                "issuer": fm.get("issuer"),
                "license": fm.get("license", "synthetic-internal"),
            }
            for opt in (
                "manufacturer", "refrigerants", "regulations", "doc_date",
                "category",
            ):
                if opt in fm:
                    entry[opt] = fm[opt]
        else:
            sidecar = path.parent / f"{path.name}.meta.yaml"
            if not sidecar.exists():
                continue
            fm = yaml.safe_load(sidecar.read_text(encoding="utf-8"))
            entry = {
                "source_id": fm["source_id"],
                "path": rel,
                "type": fm.get("type"),
                "bucket": fm.get("bucket", path.parent.name),
                "title": fm.get("title"),
                "issuer": fm.get("issuer"),
                "license": fm.get("license", "synthetic-internal"),
            }
            for opt in (
                "manufacturer", "refrigerants", "regulations", "doc_date",
                "record_count", "category",
            ):
                if opt in fm:
                    entry[opt] = fm[opt]

        if entry["source_id"] in seen_ids:
            raise ValueError(f"Duplicate source_id: {entry['source_id']} at {rel}")
        seen_ids.add(entry["source_id"])
        entries.append({k: v for k, v in entry.items() if v is not None})

    # Append reference-only real anchors.
    for anchor in REAL_ANCHORS:
        if anchor["source_id"] in seen_ids:
            continue
        entries.append(anchor)

    return {"version": 1, "sources": entries}


def write_manifest(manifest: dict[str, Any]) -> Path:
    path = SOURCES_DIR / "manifest.yaml"
    header = textwrap.dedent("""\
        # Source-corpus manifest.
        #
        # Auto-built by scripts/generate_corpus.py from per-file frontmatter
        # (markdown sources) and per-file .meta.yaml sidecars (jsonl/csv
        # sources). Real public anchors are declared in REAL_ANCHORS within
        # that script and appended with license: reference-only — they are
        # downloaded on demand by scripts/fetch_anchors.py.
        #
        # To re-build: python scripts/generate_corpus.py --manifest-only

    """)
    body = yaml.safe_dump(manifest, sort_keys=False)
    path.write_text(header + body, encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--manifest-only", action="store_true",
                        help="Skip generation; only rebuild manifest from existing files.")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    if not args.manifest_only:
        # Per-generator RNGs derived from the master seed so bumping one
        # generator's count doesn't shift filenames in the others.
        rngs = {name: random.Random(f"{args.seed}:{name}") for name in
                ["tsbs", "sops", "emails", "tickets", "specs"]}

        # Wipe generator-owned files in each bucket before regenerating.
        # Hand-authored files (listed in HAND_AUTHORED) are preserved.
        for bucket, keep in HAND_AUTHORED.items():
            wiped = _wipe_generated(SOURCES_DIR / bucket, keep)
            if not args.quiet and wiped:
                print(f"wiped {wiped} prior-run files from {bucket}/")

        plan = [
            (lambda: gen_tsbs(rngs["tsbs"], SOURCES_DIR / "bulletins"), "TSBs"),
            (lambda: gen_sops(rngs["sops"], SOURCES_DIR / "sops"), "SOPs"),
            (lambda: gen_emails(rngs["emails"], SOURCES_DIR / "emails"), "emails"),
            (lambda: gen_tickets(rngs["tickets"], SOURCES_DIR / "tickets"), "ticket files"),
            (lambda: gen_specs(rngs["specs"], SOURCES_DIR / "specs"), "spec CSVs"),
        ]
        for fn, name in plan:
            paths = fn()
            if not args.quiet:
                print(f"{name}: {len(paths)} files")

    manifest = build_manifest()
    path = write_manifest(manifest)
    if not args.quiet:
        # Bucket breakdown for sanity.
        buckets: dict[str, int] = {}
        for e in manifest["sources"]:
            buckets[e["bucket"]] = buckets.get(e["bucket"], 0) + 1
        print(f"manifest: {len(manifest['sources'])} entries -> {path}")
        for b, n in sorted(buckets.items()):
            print(f"  {b}: {n}")


if __name__ == "__main__":
    main()
