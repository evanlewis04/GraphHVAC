"""Heading-aware recursive chunker.

Turns each ``Document`` into a list of ``Chunk`` records. Strategy:

  1. Parse markdown headings into a tree of sections.
  2. Walk the tree: if a section (heading + body + descendants) fits under
     ``max_tokens``, emit it as one chunk. Otherwise emit the section's
     own body first, then recurse into children.
  3. If a leaf section's body is itself over ``max_tokens``, paragraph-
     split with overlap.
  4. Combine adjacent small chunks that share a heading-path prefix so
     chunks stay dense (target ~``target_tokens``).

Token counts use tiktoken's ``cl100k_base`` — not exact for Voyage but
close enough for sizing decisions.

Each ``Chunk`` carries:
  - ``heading_path``: list of heading titles from root to the section
  - ``char_range``: (start, end) in the original document text
  - ``page_range``: (start_page, end_page) if the document has
    ``page_offsets`` in metadata (set by the PDF loader)
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from typing import Any

import tiktoken

from src.ingest.loaders.base import Document

_ENCODER = tiktoken.get_encoding("cl100k_base")
_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.MULTILINE)


@dataclass(frozen=True)
class Chunk:
    """A unit of retrievable content with stable provenance.

    ``chunk_id`` is content-hash-derived (``{source_id}:{ordinal:04d}:{short_hash}``)
    so re-ingesting unchanged content yields the same id (idempotent indexing).
    """

    chunk_id: str
    source_id: str
    ordinal: int
    content: str
    heading_path: list[str] = field(default_factory=list)
    page_range: tuple[int, int] | None = None
    char_range: tuple[int, int] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


def _ntokens(text: str) -> int:
    return len(_ENCODER.encode(text))


def _short_hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()[:10]


def _make_chunk_id(source_id: str, ordinal: int, content: str) -> str:
    safe = source_id.replace("/", "_")
    return f"{safe}:{ordinal:04d}:{_short_hash(content)}"


# ---------------------------------------------------------------------------
# Heading tree
# ---------------------------------------------------------------------------


@dataclass
class _Section:
    level: int               # 0 = root, 1 = h1, ...
    title: str
    body: str                # prose between this heading and the first child
    children: list["_Section"] = field(default_factory=list)
    start_char: int = 0
    end_char: int = 0


def _parse_sections(text: str) -> _Section:
    """Build a heading tree from markdown text."""
    root = _Section(level=0, title="", body="", start_char=0, end_char=len(text))
    stack: list[_Section] = [root]

    headings = [(m.start(), m.end(), len(m.group(1)), m.group(2).strip())
                for m in _HEADING_RE.finditer(text)]
    headings.append((len(text), len(text), 0, ""))

    if headings and headings[0][0] > 0:
        root.body = text[:headings[0][0]].strip()

    for i in range(len(headings) - 1):
        start, _, level, title = headings[i]
        next_start = headings[i + 1][0]
        nl = text.find("\n", start)
        body_start = nl + 1 if nl != -1 else start
        body = text[body_start:next_start].strip()

        section = _Section(
            level=level,
            title=title,
            body=body,
            start_char=start,
            end_char=next_start,
        )
        while stack and stack[-1].level >= level:
            stack.pop()
        if not stack:
            stack.append(root)
        stack[-1].children.append(section)
        stack.append(section)

    return root


def _section_text(section: _Section) -> str:
    """Heading + body + recursively rendered children."""
    parts: list[str] = []
    if section.level > 0:
        parts.append("#" * section.level + " " + section.title)
    if section.body:
        parts.append(section.body)
    for child in section.children:
        parts.append(_section_text(child))
    return "\n\n".join(p for p in parts if p)


# ---------------------------------------------------------------------------
# Paragraph splitter (fallback when a single leaf section is too big)
# ---------------------------------------------------------------------------


def _take_tail_tokens(text: str, n: int) -> str:
    if n <= 0:
        return ""
    tokens = _ENCODER.encode(text)
    if len(tokens) <= n:
        return text
    return _ENCODER.decode(tokens[-n:])


def _split_by_paragraphs(text: str, max_tokens: int, overlap_tokens: int) -> list[str]:
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    chunks: list[str] = []
    buffer: list[str] = []
    buffer_tokens = 0

    def _flush() -> None:
        nonlocal buffer, buffer_tokens
        if not buffer:
            return
        chunks.append("\n\n".join(buffer))
        tail = _take_tail_tokens("\n\n".join(buffer), overlap_tokens)
        buffer = [tail] if tail else []
        buffer_tokens = _ntokens(tail) if tail else 0

    for para in paragraphs:
        para_tokens = _ntokens(para)
        if para_tokens > max_tokens:
            # Hard-split: sentence by sentence.
            for sent in re.split(r"(?<=[.!?])\s+", para):
                s_tokens = _ntokens(sent)
                if buffer_tokens + s_tokens > max_tokens and buffer:
                    _flush()
                buffer.append(sent)
                buffer_tokens += s_tokens
            continue

        if buffer_tokens + para_tokens > max_tokens and buffer:
            _flush()
        buffer.append(para)
        buffer_tokens += para_tokens

    if buffer:
        chunks.append("\n\n".join(buffer))
    return chunks


# ---------------------------------------------------------------------------
# Walker + combiner
# ---------------------------------------------------------------------------


def _walk(
    section: _Section,
    path: list[str],
    out: list[tuple[str, list[str], tuple[int, int]]],
    *,
    max_tokens: int,
    overlap_tokens: int,
) -> None:
    full_text = _section_text(section)
    if _ntokens(full_text) <= max_tokens and section.level > 0:
        out.append((full_text, path[:], (section.start_char, section.end_char)))
        return

    if section.body:
        prefix = ("#" * section.level + " " + section.title + "\n\n") if section.level else ""
        body_with_heading = prefix + section.body
        if _ntokens(body_with_heading) <= max_tokens:
            out.append((body_with_heading, path[:], (section.start_char, section.start_char)))
        else:
            for piece in _split_by_paragraphs(body_with_heading, max_tokens, overlap_tokens):
                out.append((piece, path[:], (section.start_char, section.start_char)))

    for child in section.children:
        _walk(
            child,
            path + [child.title],
            out,
            max_tokens=max_tokens,
            overlap_tokens=overlap_tokens,
        )


def _combine_small(
    items: list[tuple[str, list[str], tuple[int, int]]],
    target_tokens: int,
) -> list[tuple[str, list[str], tuple[int, int]]]:
    out: list[tuple[str, list[str], tuple[int, int]]] = []
    for content, path, char_range in items:
        if not out:
            out.append((content, path, char_range))
            continue
        prev_content, prev_path, prev_range = out[-1]
        combined = prev_content + "\n\n" + content
        common = min(len(prev_path), len(path))
        share_prefix = common > 0 and prev_path[:common] == path[:common]
        if _ntokens(combined) <= target_tokens and share_prefix:
            out[-1] = (
                combined,
                prev_path if len(prev_path) <= len(path) else path,
                (prev_range[0], char_range[1]),
            )
        else:
            out.append((content, path, char_range))
    return out


def _page_range_for_char_range(
    char_range: tuple[int, int],
    page_offsets: list[tuple[int, int]] | None,
) -> tuple[int, int] | None:
    if not page_offsets:
        return None
    start_char, end_char = char_range
    start_page = page_offsets[0][0]
    end_page = page_offsets[-1][0]
    for page, offset in page_offsets:
        if offset <= start_char:
            start_page = page
        if offset <= end_char:
            end_page = page
    return (start_page, end_page)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def chunk_document(
    document: Document,
    *,
    max_tokens: int = 1000,
    target_tokens: int = 700,
    overlap_tokens: int = 100,
) -> list[Chunk]:
    text = document.content
    if not text.strip():
        return []

    root = _parse_sections(text)
    raw: list[tuple[str, list[str], tuple[int, int]]] = []
    _walk(root, [], raw, max_tokens=max_tokens, overlap_tokens=overlap_tokens)
    combined = _combine_small(raw, target_tokens)

    page_offsets = document.metadata.get("page_offsets")
    chunks: list[Chunk] = []
    for i, (content, heading_path, char_range) in enumerate(combined):
        if not content.strip():
            continue
        chunk_id = _make_chunk_id(document.source_id, i, content)
        page_range = _page_range_for_char_range(char_range, page_offsets)
        # Strip noisy fields from the per-chunk metadata copy.
        meta = {k: v for k, v in document.metadata.items() if k != "page_offsets"}
        chunks.append(Chunk(
            chunk_id=chunk_id,
            source_id=document.source_id,
            ordinal=i,
            content=content,
            heading_path=heading_path,
            page_range=page_range,
            char_range=char_range,
            metadata=meta,
        ))
    return chunks
