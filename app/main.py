from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from prometheus_fastapi_instrumentator import Instrumentator
import structlog

from app.api.notes import router as notes_router
from app.api.reminders import router as reminders_router
from app.api.sessions import router as sessions_router
from app.api.users import router as users_router
from app.core.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        description="Personal AI assistant with persistent memory, notes, and reminders.",
        version="0.1.0",
    )
    structlog.configure(processors=[structlog.processors.JSONRenderer()])

    @app.get("/health", tags=["health"])
    def health() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(sessions_router, prefix="/api/v1")
    app.include_router(users_router, prefix="/api/v1")
    app.include_router(notes_router, prefix="/api/v1")
    app.include_router(reminders_router, prefix="/api/v1")

    # Serve static chat UI
    import os

    static_dir = os.path.join(os.path.dirname(__file__), "static")
    if os.path.isdir(static_dir):
        app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

    Instrumentator().instrument(app).expose(app, include_in_schema=False)
    return app


app = create_app()
