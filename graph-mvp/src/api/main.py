"""FastAPI app entry point.

Run with::

    uvicorn src.api.main:app --reload
"""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from src.api import audit, chat

WEB_DIR = Path(__file__).resolve().parents[2] / "web"


def create_app() -> FastAPI:
    app = FastAPI(title="Graph MVP", version="0.1.0")
    app.include_router(chat.router)
    app.include_router(audit.router)
    if WEB_DIR.exists():
        app.mount("/", StaticFiles(directory=WEB_DIR, html=True), name="web")
    return app


app = create_app()
