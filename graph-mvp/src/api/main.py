"""FastAPI app entry point.

Run with::

    uvicorn src.api.main:app --reload
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from . import audit, chat


def create_app() -> FastAPI:
    app = FastAPI(title="Graph MVP", version="0.1.0")
    app.include_router(chat.router)
    app.include_router(audit.router)
    app.mount("/", StaticFiles(directory="web", html=True), name="web")
    return app


app = create_app()
