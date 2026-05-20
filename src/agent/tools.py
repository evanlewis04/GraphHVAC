"""Tool schemas (Anthropic tool-use format) and the dispatcher.

Tools split into two groups:

  - **Knowledge layer** — ``read_wiki_page``, ``search_wiki``,
    ``list_wiki_directory``. The wiki is the LLM-structured view.
  - **Retrieval layer** — ``retrieve``, ``read_source``. Hybrid
    vector + BM25 search over ingested source chunks; ``read_source``
    pulls raw text from a source document for verification.
  - **Facts layer** — ``run_sql``, ``get_schema``. DuckDB over ERP
    operational data.

Every ``retrieve`` call allocates citation_ids (``c1``, ``c2``, ...)
from a per-trace ``CitationRegistry`` carried in ``ToolContext``. The
agent loop creates one registry per run; this lets the final answer
quote ``[c1]`` and the API hand the user back the full chunk for c1.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from src.retrieval.search import RetrievedChunk, read_source, retrieve
from src.tools.sql_query import get_schema, run_sql
from src.tools.wiki_read import list_wiki_directory, read_wiki_page, search_wiki


# ---------------------------------------------------------------------------
# Citation registry + tool context
# ---------------------------------------------------------------------------


@dataclass
class CitationRegistry:
    """Per-trace map from citation_id ('c1') to retrieved chunk."""

    by_id: dict[str, RetrievedChunk] = field(default_factory=dict)
    _counter: int = 0

    def allocate(self, chunk: RetrievedChunk) -> str:
        # If this exact chunk was retrieved before in the same trace, reuse its id.
        for cid, existing in self.by_id.items():
            if existing.chunk_id == chunk.chunk_id:
                return cid
        self._counter += 1
        cid = f"c{self._counter}"
        # Stamp the citation_id onto the chunk (frozen dataclass, so we copy).
        from dataclasses import replace
        self.by_id[cid] = replace(chunk, citation_id=cid)
        return cid

    def all(self) -> list[RetrievedChunk]:
        return list(self.by_id.values())


@dataclass
class ToolContext:
    """Per-trace state threaded into every tool call."""

    citations: CitationRegistry = field(default_factory=CitationRegistry)


# ---------------------------------------------------------------------------
# Tool schemas (Anthropic tool-use format)
# ---------------------------------------------------------------------------


AGENT_TOOLS: list[dict[str, Any]] = [
    {
        "name": "retrieve",
        "description": (
            "Hybrid vector + BM25 retrieval over the ingested source corpus "
            "(manufacturer bulletins, regulatory docs, internal SOPs, supplier "
            "emails, service tickets, spec sheets). Returns up to k ranked chunks "
            "with stable citation ids (c1, c2, ...). When you use a chunk in your "
            "final answer, cite it inline as [c1], [c2], etc. Filters narrow by "
            "bucket (bulletins/sops/emails/tickets/specs/manuals), source_type, "
            "manufacturer (substring), refrigerant, source_id, or date range "
            "(date_from / date_to as ISO YYYY-MM-DD)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "k": {"type": "integer", "default": 5},
                "filters": {
                    "type": "object",
                    "properties": {
                        "bucket": {"type": "string"},
                        "source_type": {"type": "string"},
                        "manufacturer": {"type": "string"},
                        "refrigerant": {"type": "string"},
                        "source_id": {"type": "string"},
                        "date_from": {"type": "string"},
                        "date_to": {"type": "string"},
                    },
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "read_source",
        "description": (
            "Read the raw text of a source document by source_id (returned by "
            "retrieve as part of each chunk). Use this when chunk snippets aren't "
            "enough context. Returns the full document body, truncated to ~8KB."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "source_id": {"type": "string"},
                "page_range": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "minItems": 2,
                    "maxItems": 2,
                    "description": "Optional [start_page, end_page] for PDFs.",
                },
            },
            "required": ["source_id"],
        },
    },
    {
        "name": "read_wiki_page",
        "description": (
            "Read the full contents of a wiki page by its relative path "
            "(e.g. 'skus/CAP-LEN-30MFD-0001.md', 'concepts/r-410a-phase-out.md', '_index.md')."
        ),
        "input_schema": {
            "type": "object",
            "properties": {"path": {"type": "string"}},
            "required": ["path"],
        },
    },
    {
        "name": "search_wiki",
        "description": (
            "Substring search across all wiki pages. Returns matching pages with snippets. "
            "Use single keywords or short phrases - 'R-410A', 'Lennox tariff', 'capacitor'."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "limit": {"type": "integer", "default": 20},
            },
            "required": ["query"],
        },
    },
    {
        "name": "list_wiki_directory",
        "description": (
            "List the files in a wiki subdirectory. Useful starting points: '', 'skus', "
            "'suppliers', 'customers', 'warehouses', 'refrigerants', 'concepts'."
        ),
        "input_schema": {
            "type": "object",
            "properties": {"directory": {"type": "string"}},
            "required": ["directory"],
        },
    },
    {
        "name": "run_sql",
        "description": (
            "Run a read-only DuckDB SQL query. Available tables: suppliers, warehouses, skus, "
            "customers, orders, inventory. Use this for counts, sums, top-N, joins, and any "
            "numeric question. Returns at most 200 rows; aggregate or LIMIT in your query."
        ),
        "input_schema": {
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"],
        },
    },
    {
        "name": "get_schema",
        "description": "Get the column-and-type list for one DuckDB table.",
        "input_schema": {
            "type": "object",
            "properties": {"table": {"type": "string"}},
            "required": ["table"],
        },
    },
]


# ---------------------------------------------------------------------------
# Tool result formatting
# ---------------------------------------------------------------------------


def _format_retrieve_result(
    query: str,
    chunks: list[RetrievedChunk],
    registry: CitationRegistry,
) -> str:
    if not chunks:
        return f'No chunks matched query "{query}".'
    lines = [f'Retrieved {len(chunks)} chunks for query "{query}":\n']
    for chunk in chunks:
        cid = registry.allocate(chunk)
        head = " > ".join(chunk.heading_path) if chunk.heading_path else "—"
        page = (
            f" page {chunk.page_range[0]}-{chunk.page_range[1]}"
            if chunk.page_range else ""
        )
        lines.append(
            f"[{cid}] {chunk.source_id}\n"
            f"      heading: {head}{page}\n"
            f"      score={chunk.score:.3f}  bm25={chunk.bm25_score:.2f}  "
            f"vec={chunk.vector_score:.2f}"
            + (f"  rerank={chunk.rerank_score:.2f}" if chunk.rerank_score is not None else "")
            + f"\n      {chunk.snippet}\n"
        )
    lines.append(
        "When you use any of these chunks in your answer, cite them inline as [c1], [c2], etc."
    )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Dispatcher
# ---------------------------------------------------------------------------


def execute_tool(
    name: str,
    arguments: dict[str, Any],
    context: ToolContext | None = None,
) -> str:
    """Execute a tool and return its result as a string for tool_result content.

    ``context`` is required for ``retrieve``; other tools ignore it. The
    parameter is optional so existing callers (and unit tests) that
    exercise the non-retrieval tools still work.
    """
    try:
        if name == "retrieve":
            if context is None:
                context = ToolContext()
            chunks = retrieve(
                arguments["query"],
                k=arguments.get("k", 5),
                filters=arguments.get("filters") or None,
            )
            return _format_retrieve_result(arguments["query"], chunks, context.citations)
        if name == "read_source":
            page_range = arguments.get("page_range")
            page_tuple = tuple(page_range) if page_range else None
            return read_source(arguments["source_id"], page_range=page_tuple)
        if name == "read_wiki_page":
            return read_wiki_page(arguments["path"])
        if name == "search_wiki":
            results = search_wiki(arguments["query"], arguments.get("limit", 20))
            return json.dumps(results, indent=2)
        if name == "list_wiki_directory":
            return json.dumps(list_wiki_directory(arguments["directory"]), indent=2)
        if name == "run_sql":
            rows = run_sql(arguments["query"])
            return json.dumps(rows, indent=2, default=str)
        if name == "get_schema":
            return json.dumps(get_schema(arguments["table"]), indent=2)
        return f"ERROR: unknown tool {name}"
    except Exception as exc:  # surface failures to the model so it can adapt
        return f"ERROR: {type(exc).__name__}: {exc}"
