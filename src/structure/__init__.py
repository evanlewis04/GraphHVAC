"""Knowledge structurer.

Turns the retrieval-side chunk corpus into the structured markdown wiki.
For each entity type declared in ``concepts.yaml`` the builder:

  1. Retrieves chunks relevant to each entity instance
  2. Asks an LLM to synthesize a wiki page with inline ``[chunk_id]``
     citations
  3. Validates that every claim has a citation and no entity ids were
     invented
  4. Writes the page to ``data/wiki/...`` with frontmatter recording
     provenance, freshness, and template version

Freshness tracking lives in ``freshness.py``; the health-check pass
(contradictions, orphan chunks, thin coverage) lives in ``health.py``.
"""
