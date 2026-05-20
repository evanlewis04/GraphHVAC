"""Fetch real public-anchor source documents.

The manifest declares a handful of real regulatory / standards PDFs with
``license: reference-only``. They are NOT checked into the repo because
redistribution rights are uncertain even for nominally-public files.

This script downloads them on demand into ``data/sources/bulletins/``.
Idempotent: skips downloads when the local file already exists with a
non-zero size.

Usage:
    python scripts/fetch_anchors.py
    python scripts/fetch_anchors.py --force        # re-download even if present
    python scripts/fetch_anchors.py --list         # just list, don't download

Network access required. If a URL has rotted, this script will print the
broken URL and skip; the manifest still references it for traceability.
"""

from __future__ import annotations

import argparse
import sys
import urllib.error
import urllib.request
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SOURCES_DIR = ROOT / "data" / "sources"


def load_anchors() -> list[dict]:
    manifest_path = SOURCES_DIR / "manifest.yaml"
    if not manifest_path.exists():
        print(f"manifest.yaml not found at {manifest_path}", file=sys.stderr)
        sys.exit(1)
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    return [e for e in manifest.get("sources", []) if e.get("license") == "reference-only"]


def fetch(anchor: dict, *, force: bool, quiet: bool) -> tuple[str, str]:
    """Returns (status, message)."""
    target = SOURCES_DIR / anchor["path"]
    target.parent.mkdir(parents=True, exist_ok=True)
    url = anchor.get("fetch")
    if not url:
        return ("skip", "no fetch URL")
    if target.exists() and target.stat().st_size > 0 and not force:
        return ("skip", f"already present ({target.stat().st_size} bytes)")

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "graph-fetch-anchors/1.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
        return ("error", f"{type(exc).__name__}: {exc}")

    target.write_bytes(data)
    return ("ok", f"{len(data)} bytes")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--list", action="store_true",
                        help="List anchors and exit; don't download.")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    anchors = load_anchors()
    if not anchors:
        print("No reference-only anchors found in manifest.")
        return

    if args.list:
        for a in anchors:
            print(f"{a['source_id']}  ->  {a.get('fetch', '(no fetch URL)')}")
        return

    for anchor in anchors:
        status, msg = fetch(anchor, force=args.force, quiet=args.quiet)
        if not args.quiet or status != "skip":
            print(f"[{status}] {anchor['source_id']}: {msg}")


if __name__ == "__main__":
    main()
