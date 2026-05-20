"""Email-thread loader.

Our synthetic supplier email threads are markdown files where each
message is delimited by a horizontal-rule line (``---``) and starts
with ``From:`` / ``To:`` / ``Date:`` / ``Subject:`` header lines.

This loader splits a thread into one ``Document`` per message so
retrieval can cite a specific sender + date rather than the whole
thread. The thread's manifest ``source_id`` is suffixed with
``#msg-{n}`` for each message.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from src.ingest.loaders.base import Document

_FRONTMATTER_RE = re.compile(r"^---\n.*?\n---\n", re.DOTALL)
_HEADER_LINE_RE = re.compile(r"^\*\*(?P<key>From|To|Cc|Date|Subject):\*\*\s*(?P<val>.+)$")


def _strip_md_emphasis(s: str) -> str:
    return s.strip().strip("*").strip()


def _parse_message(block: str) -> dict[str, str]:
    """Return {from, to, cc, date, subject, body} from one message block."""
    headers: dict[str, str] = {}
    body_lines: list[str] = []
    in_body = False
    for line in block.splitlines():
        if not in_body:
            m = _HEADER_LINE_RE.match(line.strip())
            if m:
                headers[m.group("key").lower()] = _strip_md_emphasis(m.group("val"))
                continue
            if line.strip() == "":
                # blank line after headers -> body starts
                if headers:
                    in_body = True
                    continue
        body_lines.append(line)
    headers["body"] = "\n".join(body_lines).strip()
    return headers


def load(path: Path, source_id: str, manifest_entry: dict[str, Any]) -> list[Document]:
    raw = path.read_text(encoding="utf-8")
    body = _FRONTMATTER_RE.sub("", raw, count=1).lstrip("\n")

    # Split on lines that are ONLY '---' (the message delimiter we use).
    # Filter empties caused by leading/trailing delimiters.
    blocks = [b.strip() for b in re.split(r"(?m)^---\s*$", body) if b.strip()]

    docs: list[Document] = []
    msg_idx = 0
    for block in blocks:
        # Only count blocks that actually look like a message (have a From: header).
        if not _HEADER_LINE_RE.search(block):
            # Could be a leading "# Title" or a trailing "internal note" block;
            # attach as context to the most recent message if any, otherwise skip.
            if docs:
                prev = docs[-1]
                merged = prev.content + "\n\n---\n\n" + block
                docs[-1] = Document(prev.source_id, merged, prev.metadata)
            continue
        msg_idx += 1
        parsed = _parse_message(block)
        rendered = (
            f"From: {parsed.get('from', '?')}\n"
            f"To: {parsed.get('to', '?')}\n"
            f"Date: {parsed.get('date', '?')}\n"
            f"Subject: {parsed.get('subject', '?')}\n\n"
            f"{parsed.get('body', '')}"
        )
        metadata = {
            "source_path": str(path),
            "source_type": "email",
            "bucket": manifest_entry.get("bucket"),
            "title": manifest_entry.get("title"),
            "issuer": manifest_entry.get("issuer"),
            "manufacturer": manifest_entry.get("manufacturer"),
            "doc_date": manifest_entry.get("doc_date"),
            "license": manifest_entry.get("license"),
            "thread_id": source_id,
            "msg_index": msg_idx,
            "sender": parsed.get("from"),
            "subject": parsed.get("subject"),
            "msg_date": parsed.get("date"),
        }
        metadata = {k: v for k, v in metadata.items() if v is not None}
        docs.append(Document(
            source_id=f"{source_id}#msg-{msg_idx}",
            content=rendered,
            metadata=metadata,
        ))

    if not docs:
        # Fallback: thread had no recognizable headers (e.g. simple md note).
        # Emit a single Document with the whole body so we don't lose the file.
        docs.append(Document(
            source_id=source_id,
            content=body,
            metadata={
                "source_path": str(path),
                "source_type": "email",
                "bucket": manifest_entry.get("bucket"),
                "title": manifest_entry.get("title"),
            },
        ))
    return docs
