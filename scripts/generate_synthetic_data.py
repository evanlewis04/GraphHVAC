"""Generate synthetic HVAC distributor CSVs into ``data/raw/``.

Usage:
    python scripts/generate_synthetic_data.py [--seed 42]
"""

from __future__ import annotations

import argparse

from src.config import load_settings
from src.ingest.synthetic import generate


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    settings = load_settings()
    generate(settings.raw_dir, seed=args.seed)


if __name__ == "__main__":
    main()
