"""Hybrid retrieval over the ingested source corpus.

Split into two modules:

  - ``index.py``  — write path. Persists chunks + vectors to LanceDB and
                    builds an in-process BM25 index.
  - ``search.py`` — read path. ``retrieve(query, k, filters)`` returns
                    ranked chunks with citation ids and scores.

The agent calls ``search.retrieve`` via the ``retrieve`` tool registered
in ``src/agent/tools.py`` (Phase 4).
"""
