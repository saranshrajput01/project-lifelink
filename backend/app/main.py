"""
Project LIFELINK — Main Application Entry Point

AI-Powered Predictive & Connected Healthcare Intelligence Platform.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import get_settings

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup & shutdown events.
    - Startup: initialize DB connections, load ML models, etc.
    - Shutdown: close connections gracefully.
    """
    # ─── Startup ───
    print(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION} starting...")
    print(f"   Environment: {settings.ENVIRONMENT}")
    print(f"   Debug: {settings.DEBUG}")
    from app.services.scheduler import start_scheduler, stop_scheduler

    start_scheduler()
    print("   ⏰ Reminder notification scheduler started")
    yield
    # ─── Shutdown ───
    stop_scheduler()
    print(f"👋 {settings.APP_NAME} shutting down...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-Powered Predictive & Connected Healthcare Intelligence Platform",
    docs_url="/docs" if settings.DEBUG else None,  # Swagger UI only in debug
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
)

# ─── CORS Middleware ───────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Register API Routes ──────────────────────────────────────────
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint — basic service info."""
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": f"{settings.API_V1_PREFIX}/docs" if settings.DEBUG else "disabled",
        "health": f"{settings.API_V1_PREFIX}/health",
    }
