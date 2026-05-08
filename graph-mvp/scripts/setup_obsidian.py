"""Seed the Obsidian vault with the committed default config.

Run automatically by ``scripts/run_full_pipeline.py``; you can also run
it on its own:

    python scripts/setup_obsidian.py
    python scripts/setup_obsidian.py --force   # reset to shipped defaults

See ``src/compile/obsidian.py`` for the design rationale.
"""

from __future__ import annotations

import argparse

from src.compile.obsidian import setup_obsidian


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--force", action="store_true",
        help="Overwrite existing .obsidian/ files with the shipped defaults.",
    )
    args = parser.parse_args()
    setup_obsidian(force=args.force)


if __name__ == "__main__":
    main()
