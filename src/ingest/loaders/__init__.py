"""Per-format source-document loaders.

Each loader module exposes ``load(path)`` returning a normalized
``Document`` (see ``base.py``). The ingest driver dispatches on the
``type`` field declared in ``data/sources/manifest.yaml``.
"""
