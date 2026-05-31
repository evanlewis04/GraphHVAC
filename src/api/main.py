"""FastAPI app entry point.

Run with::

    uvicorn src.api.main:app --reload
"""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from src.api import admin, audit, briefs, chat, workflows

WEB_DIR = Path(__file__).resolve().parents[2] / "web"


def create_app() -> FastAPI:
    app = FastAPI(title="Graph MVP", version="0.1.0")
    app.include_router(chat.router)
    app.include_router(audit.router)
    app.include_router(briefs.router)
    app.include_router(workflows.router)
    app.include_router(admin.router)

    # Browsers auto-request /favicon.ico; point it at the SVG so it's a 200,
    # not a 404. Registered before the catch-all static mount.
    @app.get("/favicon.ico", include_in_schema=False)
    def favicon():
        svg = WEB_DIR / "favicon.svg"
        if svg.exists():
            return FileResponse(svg, media_type="image/svg+xml")
        return RedirectResponse(url="/favicon.svg")

    if WEB_DIR.exists():
        app.mount("/", StaticFiles(directory=WEB_DIR, html=True), name="web")
    return app


app = create_app()
