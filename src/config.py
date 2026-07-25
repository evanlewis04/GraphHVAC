"""Centralized config: paths, model names, env loading."""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

# override=True so values in .env beat any empty/stale shell env vars.
load_dotenv(override=True)


@dataclass(frozen=True)
class Settings:
    anthropic_api_key: str
    agent_model: str
    compiler_model: str
    data_dir: Path
    wiki_dir: Path
    duckdb_path: Path
    audit_db_path: Path
    raw_dir: Path
    api_host: str
    api_port: int


def _path(env_var: str, default: str) -> Path:
    return Path(os.environ.get(env_var, default)).resolve()


@lru_cache(maxsize=1)
def load_settings() -> Settings:
    data_dir = _path("GRAPH_DATA_DIR", "./data")
    return Settings(
        anthropic_api_key=os.environ.get("ANTHROPIC_API_KEY", ""),
        agent_model=os.environ.get("GRAPH_AGENT_MODEL", "claude-sonnet-5"),
        compiler_model=os.environ.get("GRAPH_COMPILER_MODEL", "claude-haiku-4-5"),
        data_dir=data_dir,
        wiki_dir=_path("GRAPH_WIKI_DIR", str(data_dir / "wiki")),
        duckdb_path=_path("GRAPH_DUCKDB_PATH", str(data_dir / "staging.duckdb")),
        audit_db_path=_path("GRAPH_AUDIT_DB_PATH", str(data_dir / "audit.sqlite")),
        raw_dir=data_dir / "raw",
        api_host=os.environ.get("GRAPH_API_HOST", "127.0.0.1"),
        api_port=int(os.environ.get("GRAPH_API_PORT", "8000")),
    )
