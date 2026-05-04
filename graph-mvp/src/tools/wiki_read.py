"""Wiki navigation tools the agent can call.

All paths are validated to live inside ``GRAPH_WIKI_DIR`` to keep the
agent from reading arbitrary filesystem paths.
"""

from __future__ import annotations

from pathlib import Path

from src.config import load_settings


def _wiki_root() -> Path:
    return load_settings().wiki_dir


def _resolve_in_wiki(rel: str) -> Path:
    root = _wiki_root().resolve()
    candidate = (root / rel).resolve()
    if root not in candidate.parents and candidate != root:
        raise ValueError(f"Path escapes the wiki root: {rel}")
    return candidate


def read_wiki_page(path: str) -> str:
    """Read the full contents of a wiki page by its relative path."""
    target = _resolve_in_wiki(path)
    if not target.exists():
        return f"ERROR: wiki page not found: {path}"
    if target.is_dir():
        return f"ERROR: {path} is a directory; use list_wiki_directory."
    return target.read_text(encoding="utf-8")


def search_wiki(query: str, limit: int = 20) -> list[dict[str, str]]:
    """Substring search across wiki pages. Returns matching pages with snippets.

    Cheap and good enough for an MVP — no embeddings, no inverted index.
    """
    root = _wiki_root()
    needle = query.lower()
    out: list[dict[str, str]] = []
    for md in sorted(root.rglob("*.md")):
        try:
            text = md.read_text(encoding="utf-8")
        except OSError:
            continue
        idx = text.lower().find(needle)
        if idx < 0:
            continue
        start = max(0, idx - 80)
        end = min(len(text), idx + len(query) + 80)
        snippet = text[start:end].replace("\n", " ")
        out.append({
            "path": str(md.relative_to(root)),
            "snippet": ("..." if start > 0 else "") + snippet + ("..." if end < len(text) else ""),
        })
        if len(out) >= limit:
            break
    return out


def list_wiki_directory(directory: str) -> list[str]:
    """List all files (relative paths) in a wiki subdirectory."""
    target = _resolve_in_wiki(directory)
    if not target.exists() or not target.is_dir():
        return []
    root = _wiki_root()
    return sorted(str(p.relative_to(root)) for p in target.iterdir() if not p.name.startswith("."))
