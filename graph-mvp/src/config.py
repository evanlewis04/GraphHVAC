"""Centralized config: paths, model names, env loading."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    anthropic_api_key: str
    agent_model: str
    compiler_model: str
    data_dir: Path
    wiki_dir: Path
    duckdb_path: Path
    audit_db_path: Path
    api_host: str
    api_port: int


def load_settings() -> Settings:
    raise NotImplementedError
