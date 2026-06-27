"""
Demiurge Voice Platform — FastAPI Application

Entry point. Mounts all routers and initializes the platform.
"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.config import settings
from app.database import engine, Base
from app.core.logger import get_logger
from app.tools.builtin import register_builtin_tools

# Import routers
from app.routers import health, agents, calls, voices, tools, memory, analytics, campaigns, providers

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info("platform.starting", version=settings.APP_VERSION, env=settings.ENV)

    # Create database tables
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("database.tables_created")
    except Exception as e:
        logger.error("database.init_failed", error=str(e))

    # Register built-in tools
    try:
        register_builtin_tools()
        logger.info("tools.registered")
    except Exception as e:
        logger.error("tools.registration_failed", error=str(e))

    yield

    # Shutdown
    logger.info("platform.shutting_down")
    await engine.dispose()


# ── FastAPI App ────────────────────────────────────────────────────
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Self-hosted voice AI infrastructure for the Demiurge Systems ecosystem.",
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# ── CORS ───────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS.split(",") if "," in settings.ALLOWED_ORIGINS else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── API Routes ─────────────────────────────────────────────────────
app.include_router(health.router)
app.include_router(agents.router)
app.include_router(calls.router)
app.include_router(voices.router)
app.include_router(tools.router)
app.include_router(memory.router)
app.include_router(analytics.router)
app.include_router(campaigns.router)
app.include_router(providers.router)

# ── Static Files (frontend production build) ───────────────────────
frontend_build_path = os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist")
if os.path.exists(frontend_build_path):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_build_path, "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        index_path = os.path.join(frontend_build_path, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        return {"detail": "Frontend not built. Run npm run build in frontend/"}


# ── Root ───────────────────────────────────────────────────────────
@app.get("/", include_in_schema=False)
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs" if settings.DEBUG else None,
    }
