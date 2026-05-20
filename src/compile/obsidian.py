"""Seed the Obsidian vault's .obsidian/ dir with committed defaults.

Why this lives outside the wiki tree
------------------------------------
Obsidian writes back to its config files whenever the vault is opened
(JSON normalization, new default fields, any UI tweak). If we tracked
those files inside ``data/wiki/.obsidian/`` they'd show as dirty after
every vault session, polluting diffs.

So:
  - Canonical defaults live in   ``data/obsidian-defaults/``   (tracked)
  - Per-machine config lives in  ``data/wiki/.obsidian/``      (gitignored)
  - ``setup_obsidian()`` copies defaults in only when the target file
    doesn't already exist, so user tweaks are never clobbered.

The pipeline runner calls this automatically after every compile.
"""

from __future__ import annotations

import shutil

from src.config import load_settings


def setup_obsidian(force: bool = False, quiet: bool = False) -> dict[str, str]:
    """Copy any missing default config into the vault's .obsidian/ dir.

    Returns a ``{filename: action}`` map. Action is one of:
      - ``copied``       — file didn't exist; we wrote the default
      - ``skipped``      — file already existed; left as-is
      - ``overwritten``  — file existed but ``force=True``; we replaced it
    """
    settings = load_settings()
    src_dir = settings.data_dir / "obsidian-defaults"
    dst_dir = settings.wiki_dir / ".obsidian"

    if not src_dir.exists():
        if not quiet:
            print(f"No defaults found at {src_dir}; nothing to seed.")
        return {}

    dst_dir.mkdir(parents=True, exist_ok=True)
    actions: dict[str, str] = {}
    for src in sorted(src_dir.glob("*.json")):
        dst = dst_dir / src.name
        if dst.exists() and not force:
            actions[src.name] = "skipped"
            continue
        existed = dst.exists()
        shutil.copy2(src, dst)
        actions[src.name] = "overwritten" if existed else "copied"

    if not quiet:
        for name, action in actions.items():
            print(f"  [{action}] {dst_dir / name}")
    return actions
