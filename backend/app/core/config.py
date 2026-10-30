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
    DATABASE_URL: str = (
        "postgresql+asyncpg://lifelink:lifelink@localhost:5432/lifelink_db"
    )
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10

    # ─── Redis ─────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"

    # ─── JWT Auth ──────────────────────────────────────────
    SECRET_KEY: str = "CHANGE-THIS-IN-PRODUCTION-USE-A-REAL-SECRET-KEY"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"

    # ─── Object storage (S3 API): Supabase Storage / MinIO ─
    S3_ENDPOINT_URL: str = "http://localhost:9000"
    S3_ACCESS_KEY: str = "minioadmin"
    S3_SECRET_KEY: str = "minioadmin"
    S3_BUCKET_NAME: str = "lifelink-documents"
    S3_REGION: str = "us-east-1"

    # ─── AI / LLM ─────────────────────────────────────────
    # Groq is the active provider (ported from bizmind-ai).
    # OpenAI/Gemini kept only as legacy/optional fallback config.
    OPENAI_API_KEY: str = ""
    GEMINI_API_KEY: str = ""

    # Groq — up to 7 keys with automatic rotation on rate limit (429)
    GROQ_API_KEY: str = ""
    GROQ_API_KEY_2: str = ""
    GROQ_API_KEY_3: str = ""
    GROQ_API_KEY_4: str = ""
    GROQ_API_KEY_5: str = ""
    GROQ_API_KEY_6: str = ""
    GROQ_API_KEY_7: str = ""
    GROQ_MODEL: str = "qwen/qwen3.8-27b"
    GROQ_MODEL_STRONG: str = "qwen/qwen3.8-27b"

    LLM_MODEL: str = "qwen/qwen3.8-27b"  # Active model (Groq)
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    # torch + MiniLM need ~500MB RAM; set false on 512MB hosts (Render free).
    # Chat then falls back to summary-context instead of vector RAG.
    ENABLE_LOCAL_EMBEDDINGS: bool = True

    @property
    def groq_api_keys(self) -> list[str]:
        """Return all configured Groq API keys (non-empty)."""
        keys = [
            self.GROQ_API_KEY,
            self.GROQ_API_KEY_2,
            self.GROQ_API_KEY_3,
            self.GROQ_API_KEY_4,
            self.GROQ_API_KEY_5,
            self.GROQ_API_KEY_6,
            self.GROQ_API_KEY_7,
        ]
        return [k for k in keys if k]

    # ─── OCR ───────────────────────────────────────────────
    OCR_ENGINE: str = "paddleocr"  # paddleocr | tesseract
    # PaddleOCR is too heavy for 512MB hosts; text PDFs still work via PyMuPDF.
    ENABLE_LOCAL_OCR: bool = True

    # ─── Email (SMTP) ─────────────────────────────────────
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASS: str = ""
    SMTP_FROM: str = "Project LIFELINK <noreply@lifelink.com>"

    @property
    def email_enabled(self) -> bool:
        return bool(
            self.BREVO_API_KEY or (self.SMTP_HOST and self.SMTP_USER and self.SMTP_PASS)
        )

    # Brevo HTTPS email API (needed on Render free tier: SMTP ports are blocked)
    BREVO_API_KEY: str = ""
    BREVO_SENDER_EMAIL: str = ""  # must be a verified sender in Brevo

    # ─── Celery (Background Tasks) ────────────────────────
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance — loaded once, reused everywhere."""
    return Settings()
