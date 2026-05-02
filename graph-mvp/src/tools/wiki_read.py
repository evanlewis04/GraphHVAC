"""Wiki navigation tools the agent can call.

All paths are validated to live inside ``GRAPH_WIKI_DIR`` to keep the
agent from reading arbitrary filesystem paths.
"""

from __future__ import annotations

from pathlib import Path


def read_wiki_page(path: str) -> str:
    raise NotImplementedError


def search_wiki(query: str, limit: int = 20) -> list[dict[str, str]]:
    raise NotImplementedError


def list_wiki_directory(directory: str) -> list[str]:
    raise NotImplementedError
