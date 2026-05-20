"""LLM narrative generation for SKU pages, with a content-keyed cache.

For each SKU we ask the configured compiler model (default
``claude-haiku-4-5``) to produce:
  - a 2-3 sentence description grounded in the structured fields
  - regulatory/refrigerant notes when the SKU is tied to one
  - 3-5 substitute SKU ids (chosen from a candidate set we provide)

Results are cached in ``data/narrative_cache.sqlite`` keyed by a hash of
the SKU fields + candidate ids + a template version, so re-running the
pipeline is free until inputs change.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import anthropic

from src.config import load_settings

TEMPLATE_VERSION = 1

NARRATIVE_SYSTEM_PROMPT = """\
You are writing wiki entries for a HVAC parts distributor's living
operational wiki. The reader is an operations partner or platform CEO
trying to understand a single SKU at a glance.

For each SKU, return JSON matching the provided schema with:
- description: 2-3 sentences. State what the part is, what equipment it
  goes in, and any notable spec. Plain text, no marketing fluff, no
  invented attributes. Lean on the structured fields you're given.
- regulatory_notes: only populate when the refrigerant or category warrants
  it (R-22 phased out, R-410A under HFC phase-down, R-32/R-454B as
  replacements, control board / capacitor regulatory irrelevance). Use null
  otherwise. One sentence max.
- substitutes: pick 3-5 SKU ids from the candidate list whose
  manufacturer/sub-type/spec is closest to this SKU. Each entry needs a
  one-line rationale. If no candidate is a credible substitute, return [].

Stick strictly to the candidate ids provided - never invent a SKU id.
"""

NARRATIVE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "description": {"type": "string"},
        "regulatory_notes": {"type": ["string", "null"]},
        "substitutes": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "sku_id": {"type": "string"},
                    "rationale": {"type": "string"},
                },
                "required": ["sku_id", "rationale"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["description", "regulatory_notes", "substitutes"],
    "additionalProperties": False,
}


@dataclass
class Narrative:
    description: str
    regulatory_notes: str | None
    substitutes: list[dict[str, str]]

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Narrative":
        return cls(
            description=d.get("description", "").strip(),
            regulatory_notes=(d.get("regulatory_notes") or None),
            substitutes=[
                {"sku_id": s["sku_id"], "rationale": s["rationale"]}
                for s in d.get("substitutes", [])
            ],
        )


class NarrativeCache:
    """Append-only content-keyed cache. Survives across pipeline runs."""

    def __init__(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(path)
        self._conn.execute(
            "CREATE TABLE IF NOT EXISTS narrative_cache ("
            "  cache_key TEXT PRIMARY KEY,"
            "  payload_json TEXT NOT NULL,"
            "  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP"
            ")"
        )

    def get(self, key: str) -> dict[str, Any] | None:
        row = self._conn.execute(
            "SELECT payload_json FROM narrative_cache WHERE cache_key = ?", (key,)
        ).fetchone()
        return json.loads(row[0]) if row else None

    def set(self, key: str, payload: dict[str, Any]) -> None:
        self._conn.execute(
            "INSERT OR REPLACE INTO narrative_cache (cache_key, payload_json) VALUES (?, ?)",
            (key, json.dumps(payload)),
        )
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()


def _cache_key(sku: dict[str, Any], candidate_ids: list[str]) -> str:
    payload = {
        "v": TEMPLATE_VERSION,
        "sku_id": sku["id"],
        "name": sku["name"],
        "manufacturer": sku["manufacturer"],
        "category": sku["category"],
        "sub_type": sku["sub_type"],
        "refrigerant": sku.get("refrigerant") or "",
        "candidates": sorted(candidate_ids),
    }
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True).encode("utf-8")
    ).hexdigest()


def _build_user_message(sku: dict[str, Any], candidates: list[dict[str, Any]]) -> str:
    return json.dumps(
        {
            "sku": {
                "id": sku["id"],
                "name": sku["name"],
                "manufacturer": sku["manufacturer"],
                "category": sku["category"],
                "sub_type": sku["sub_type"],
                "refrigerant": sku.get("refrigerant") or None,
            },
            "candidate_substitutes": [
                {
                    "id": c["id"],
                    "name": c["name"],
                    "manufacturer": c["manufacturer"],
                    "sub_type": c["sub_type"],
                }
                for c in candidates
            ],
        },
        indent=2,
    )


def enrich_sku(
    sku: dict[str, Any],
    candidates: list[dict[str, Any]],
    cache: NarrativeCache,
    client: anthropic.Anthropic,
    model: str,
) -> Narrative:
    candidate_ids = [c["id"] for c in candidates]
    key = _cache_key(sku, candidate_ids)
    cached = cache.get(key)
    if cached is not None:
        return Narrative.from_dict(cached)

    response = client.messages.create(
        model=model,
        max_tokens=600,
        system=NARRATIVE_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": _build_user_message(sku, candidates)}],
        output_config={
            "format": {"type": "json_schema", "schema": NARRATIVE_SCHEMA},
        },
    )
    text = next(b.text for b in response.content if b.type == "text")
    parsed = json.loads(text)

    # Filter substitutes the model invented (defense-in-depth — schema doesn't enforce id membership).
    valid_ids = set(candidate_ids)
    parsed["substitutes"] = [
        s for s in parsed.get("substitutes", []) if s.get("sku_id") in valid_ids
    ]

    cache.set(key, parsed)
    return Narrative.from_dict(parsed)


def make_client() -> anthropic.Anthropic:
    settings = load_settings()
    if not settings.anthropic_api_key:
        raise RuntimeError(
            "ANTHROPIC_API_KEY is not set; cannot run LLM narrative enrichment. "
            "Set the env var or pass --enrich-sku-limit 0 to skip."
        )
    return anthropic.Anthropic(api_key=settings.anthropic_api_key)
