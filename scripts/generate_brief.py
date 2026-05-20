"""Generate today's daily brief.

Usage:
    python scripts/generate_brief.py
    python scripts/generate_brief.py --date 2026-05-03

Requires ANTHROPIC_API_KEY. Designed to run on a cron, but useful
on-demand for demos.
"""

from __future__ import annotations

import argparse
import sys
from datetime import date

from src.briefs.generator import generate_brief


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--date", default=None,
        help="ISO date (YYYY-MM-DD); defaults to today.",
    )
    args = parser.parse_args()

    target = date.fromisoformat(args.date) if args.date else None
    try:
        path = generate_brief(target)
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
