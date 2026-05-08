"""Tests for the Obsidian config seeding behavior."""

from __future__ import annotations

import os

import pytest


@pytest.fixture
def isolated(tmp_path, monkeypatch):
    monkeypatch.setenv("GRAPH_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("GRAPH_WIKI_DIR", str(tmp_path / "wiki"))
    monkeypatch.setenv("GRAPH_DUCKDB_PATH", str(tmp_path / "staging.duckdb"))
    monkeypatch.setenv("GRAPH_AUDIT_DB_PATH", str(tmp_path / "audit.sqlite"))
    from src import config
    config.load_settings.cache_clear()
    settings = config.load_settings()
    # Create defaults directory with two example files
    (settings.data_dir / "obsidian-defaults").mkdir(parents=True, exist_ok=True)
    (settings.data_dir / "obsidian-defaults" / "graph.json").write_text('{"v": 1}')
    (settings.data_dir / "obsidian-defaults" / "app.json").write_text('{"v": 1}')
    yield settings
    config.load_settings.cache_clear()


def test_copy_seeds_missing_files(isolated):
    from src.compile.obsidian import setup_obsidian

    actions = setup_obsidian(quiet=True)
    assert actions == {"app.json": "copied", "graph.json": "copied"}
    target_dir = isolated.wiki_dir / ".obsidian"
    assert (target_dir / "graph.json").read_text() == '{"v": 1}'
    assert (target_dir / "app.json").read_text() == '{"v": 1}'


def test_skip_existing_without_force(isolated):
    """User tweaks must never be clobbered on re-run."""
    from src.compile.obsidian import setup_obsidian

    setup_obsidian(quiet=True)
    target = isolated.wiki_dir / ".obsidian" / "graph.json"
    target.write_text('{"v": 99, "user_tweak": true}')

    actions = setup_obsidian(quiet=True)
    assert actions["graph.json"] == "skipped"
    assert "user_tweak" in target.read_text()


def test_force_overwrites(isolated):
    from src.compile.obsidian import setup_obsidian

    setup_obsidian(quiet=True)
    target = isolated.wiki_dir / ".obsidian" / "graph.json"
    target.write_text('{"tampered": true}')

    actions = setup_obsidian(force=True, quiet=True)
    assert actions["graph.json"] == "overwritten"
    assert target.read_text() == '{"v": 1}'


def test_no_defaults_dir_returns_empty(isolated):
    """If the defaults dir is missing, return empty map without crashing."""
    from src.compile.obsidian import setup_obsidian

    import shutil
    shutil.rmtree(isolated.data_dir / "obsidian-defaults")

    assert setup_obsidian(quiet=True) == {}
