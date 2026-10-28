"""Tests for the LLM narrative pass.

Uses a fake Anthropic client so we can verify the full enrichment path
(cache, schema validation, SKU page rendering, candidate filtering)
without any network calls or API key.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest


@dataclass
class _Block:
    text: str
    type: str = "text"


@dataclass
class _Response:
    content: list[_Block]


class FakeClient:
    """Records every call and returns scripted JSON responses.

    Each `responses` entry is a dict matching the SKU narrative schema.
    """

    def __init__(self, responses: list[dict[str, Any]]) -> None:
        self._responses = list(responses)
        self.calls: list[dict[str, Any]] = []

        client = self  # for closure

        class _Messages:
            def create(self_inner, **kwargs):  # noqa: N805 - matches SDK signature
                client.calls.append(kwargs)
                if not client._responses:
                    raise AssertionError("FakeClient ran out of scripted responses")
                payload = client._responses.pop(0)
                return _Response(content=[_Block(text=json.dumps(payload))])

        self.messages = _Messages()


@pytest.fixture(scope="module")
def isolated_pipeline(tmp_path_factory):
    import os

    tmp = tmp_path_factory.mktemp("narrative")
    os.environ["GRAPH_DATA_DIR"] = str(tmp)
    os.environ["GRAPH_WIKI_DIR"] = str(tmp / "wiki")
    os.environ["GRAPH_DUCKDB_PATH"] = str(tmp / "staging.duckdb")
    os.environ["GRAPH_AUDIT_DB_PATH"] = str(tmp / "audit.sqlite")
    from src import config
    config.load_settings.cache_clear()
    settings = config.load_settings()

    from src.ingest.csv_loader import load_csvs
    from src.ingest.synthetic import generate

    generate(settings.raw_dir, seed=11)
    conn = load_csvs(settings.raw_dir, settings.duckdb_path)
    return settings, conn


def test_cache_roundtrip(tmp_path: Path):
    from src.compile.narrative import NarrativeCache
    cache = NarrativeCache(tmp_path / "cache.sqlite")
    assert cache.get("missing") is None
    cache.set("k", {"description": "hi", "regulatory_notes": None, "substitutes": []})
    assert cache.get("k")["description"] == "hi"


def test_enrich_caches_response(tmp_path: Path):
    from src.compile.narrative import Narrative, NarrativeCache, enrich_sku

    sku = {
        "id": "CAP-LEN-30MFD-0001", "name": "Lennox Run Capacitor 30MFD",
        "manufacturer": "Lennox", "category": "Capacitor",
        "sub_type": "Run", "refrigerant": None,
    }
    candidates = [
        {"id": "CAP-CAR-30MFD-0002", "name": "Carrier Run 30MFD",
         "manufacturer": "Carrier", "sub_type": "Run"},
        {"id": "CAP-TRA-30MFD-0003", "name": "Trane Run 30MFD",
         "manufacturer": "Trane", "sub_type": "Run"},
    ]
    fake = FakeClient([
        {
            "description": "Lennox 30µF run capacitor for residential AC condenser fan motors.",
            "regulatory_notes": None,
            "substitutes": [
                {"sku_id": "CAP-CAR-30MFD-0002", "rationale": "Same MFD/sub-type, different mfr."},
            ],
        }
    ])
    cache = NarrativeCache(tmp_path / "cache.sqlite")

    n1 = enrich_sku(sku, candidates, cache, fake, "claude-haiku-4-5")
    assert isinstance(n1, Narrative)
    assert n1.description.startswith("Lennox 30")
    assert len(n1.substitutes) == 1

    # Second call should be a cache hit -- no new API call.
    n2 = enrich_sku(sku, candidates, cache, fake, "claude-haiku-4-5")
    assert n2.description == n1.description
    assert len(fake.calls) == 1, "second call should hit the cache"


def test_invented_substitute_ids_are_dropped(tmp_path: Path):
    from src.compile.narrative import NarrativeCache, enrich_sku

    sku = {"id": "X", "name": "x", "manufacturer": "M", "category": "C",
           "sub_type": "S", "refrigerant": None}
    candidates = [{"id": "REAL-1", "name": "n", "manufacturer": "m", "sub_type": "s"}]
    fake = FakeClient([
        {
            "description": "d",
            "regulatory_notes": None,
            "substitutes": [
                {"sku_id": "REAL-1", "rationale": "ok"},
                {"sku_id": "FAKE-XYZ", "rationale": "model invented this"},
            ],
        }
    ])
    cache = NarrativeCache(tmp_path / "cache.sqlite")
    n = enrich_sku(sku, candidates, cache, fake, "claude-haiku-4-5")
    assert [s["sku_id"] for s in n.substitutes] == ["REAL-1"]


def test_sku_page_includes_llm_narrative(isolated_pipeline):
    """Run the SKU page generator with a fake enricher; verify the rendered
    page picks up the LLM-written description and substitutes."""
    from src.compile.sku_pages import generate_all
    from src.compile.narrative import Narrative

    settings, conn = isolated_pipeline
    wiki_dir = settings.wiki_dir / "_test_enriched"

    def fake_enricher(sku, candidates):
        return Narrative(
            description=f"FAKE-LLM-DESC for {sku['id']}.",
            regulatory_notes="FAKE-REG-NOTE." if sku["category"] == "Refrigerant" else None,
            substitutes=[{"sku_id": candidates[0]["id"], "rationale": "Closest match."}]
            if candidates else [],
        )

    generate_all(conn, wiki_dir, enricher=fake_enricher, enrich_limit=10)

    md_files = sorted((wiki_dir / "skus").glob("*.md"))
    assert len(md_files) > 100  # all SKUs written
    enriched = [p for p in md_files if "FAKE-LLM-DESC" in p.read_text(encoding="utf-8")]
    assert len(enriched) == 10  # only first 10 enriched, rest fall back

    sample = enriched[0].read_text(encoding="utf-8")
    assert "llm_enriched: true" in sample
    assert "## Substitutes" in sample
    assert "Closest match." in sample
