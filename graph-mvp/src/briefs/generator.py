"""Daily executive brief generator.

Runs the agent against a fixed prompt and writes the answer to
``data/briefs/YYYY-MM-DD.md``. This is the leave-behind artifact for
PE operating partners — what would land in their inbox at 7am.

The script is deliberately a thin wrapper around the existing agent
loop: same audit trail, same tool surface, same trust model.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

from src.agent.loop import run_agent
from src.config import load_settings

DAILY_BRIEF_PROMPT = """\
Generate a concise daily operations brief for our HVAC distribution platform.
Write for a PE operating partner — they want signal, not noise.

Cover:
1. **Refrigerant exposure** — current dollar exposure to R-410A and R-22 phase-out;
   any customers concentrated above $50K in 24-month revenue from phase-out SKUs.
2. **Top 3 customers by revenue** — name, segment, region, revenue.
3. **Supplier concentration risk** — any single supplier carrying more than
   25% of a category's revenue.
4. **Inventory health** — categories at any warehouse with notable stock-out risk
   (units below half the typical reorder point).

Use real numbers from the data. Cite the wiki pages and SQL queries you used.
Keep the brief under 400 words. Use markdown headings and bullet points.
"""


def briefs_dir() -> Path:
    return load_settings().data_dir / "briefs"


def generate_brief(target_date: date | None = None) -> Path:
    """Run the agent, write the answer to data/briefs/YYYY-MM-DD.md.
    Returns the path of the written brief."""
    target = target_date or date.today()
    out_dir = briefs_dir()
    out_dir.mkdir(parents=True, exist_ok=True)

    result = run_agent(DAILY_BRIEF_PROMPT)
    body = (
        f"---\n"
        f"date: {target.isoformat()}\n"
        f"trace_id: {result.trace_id}\n"
        f"iterations: {result.iterations}\n"
        f"---\n\n"
        f"# Daily Brief — {target.strftime('%A, %B %-d, %Y')}\n\n"
        f"{result.answer}\n"
    )
    path = out_dir / f"{target.isoformat()}.md"
    path.write_text(body, encoding="utf-8")
    return path


def list_briefs() -> list[dict]:
    """Return brief metadata sorted newest-first."""
    out_dir = briefs_dir()
    if not out_dir.exists():
        return []
    rows = []
    for p in sorted(out_dir.glob("*.md"), reverse=True):
        rows.append({"date": p.stem, "path": p.name, "size_bytes": p.stat().st_size})
    return rows


def read_brief(date_str: str) -> str | None:
    """Read a brief by ISO date string. Returns None if not found.
    The date_str is validated to prevent path traversal."""
    if not date_str.replace("-", "").isdigit() or len(date_str) != 10:
        return None
    p = briefs_dir() / f"{date_str}.md"
    if not p.exists():
        return None
    return p.read_text(encoding="utf-8")
