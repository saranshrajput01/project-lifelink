"""
Core configuration — loads all settings from environment variables.
Uses Pydantic Settings for type-safe config management.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from .env file or environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ─── App ───────────────────────────────────────────────
    APP_NAME: str = "Project LIFELINK"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"  # development | staging | production

    # ─── API ───────────────────────────────────────────────
    API_V1_PREFIX: str = "/api/v1"
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]  # Vite dev server

    # ─── Database (PostgreSQL + pgvector) ──────────────────
    DATABASE_URL: str = "postgresql+asyncpg://lifelink:lifelink@localhost:5432/lifelink_db"
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10

    # ─── Redis ─────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"

    # ─── JWT Auth ──────────────────────────────────────────
    SECRET_KEY: str = "CHANGE-THIS-IN-PRODUCTION-USE-A-REAL-SECRET-KEY"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"

    # ─── AWS S3 / MinIO ───────────────────────────────────
    S3_ENDPOINT_URL: str = "http://localhost:9000"
    S3_ACCESS_KEY: str = "minioadmin"
    S3_SECRET_KEY: str = "minioadmin"
    S3_BUCKET_NAME: str = "lifelink-documents"
    S3_REGION: str = "us-east-1"

    # ─── AI / LLM ─────────────────────────────────────────
    OPENAI_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    LLM_MODEL: str = "gemini-1.5-flash"  # Default model for cost efficiency
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

    # ─── OCR ───────────────────────────────────────────────
    OCR_ENGINE: str = "paddleocr"  # paddleocr | tesseract

    # ─── Celery (Background Tasks) ────────────────────────
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance — loaded once, reused everywhere."""
    return Settings()
