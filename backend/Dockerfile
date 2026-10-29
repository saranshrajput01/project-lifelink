# syntax=docker/dockerfile:1.4
# ─── Project LIFELINK Backend ───
# Multi-stage build for smaller production image

FROM python:3.11-slim as base

# Set environment
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies (asyncpg/pillow build, plus runtime libs that
# opencv/PaddleOCR (libGL, libglib) and torch (libgomp) need at import time).
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies. A BuildKit cache mount on pip's download cache
# (/root/.cache/pip) means the heavy wheels (torch ~159MB, paddle, transformers)
# are downloaded ONCE and reused on every subsequent rebuild — even when an
# earlier layer (e.g. apt) changes and invalidates these layers. So no repeated
# ~1GB downloads. (Requires DOCKER_BUILDKIT=1, which is default on this Docker.)
#
# torch: install the CPU-ONLY build from PyTorch's cpu index. The default PyPI
# aarch64 wheel (torch-2.14.1) bundles CUDA preload logic and crashes at import
# with "libcublasLt.so not found" on a CPU host. The +cpu wheel (~159MB) has no
# CUDA deps and imports cleanly. --no-deps so it can't drag in CUDA nvidia wheels;
# torch's lightweight pure-Python runtime deps are supplied via requirements.txt.
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-deps --timeout 120 --retries 10 \
    --index-url https://download.pytorch.org/whl/cpu 'torch==2.14.1+cpu'
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --timeout 120 --retries 10 -r requirements.txt
# Install sentence-transformers WITHOUT deps so it can't re-pull torch + CUDA wheels;
# its real runtime deps are already satisfied via requirements.txt above.
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-deps sentence-transformers==3.1.0

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run with uvicorn. Render (and most PaaS) inject a dynamic $PORT; fall back to
# 8000 for local/docker-compose. No --reload in production (dev-only; wastes
# memory and restarts workers on the free tier). Migrations are applied
# separately (alembic upgrade head) against the managed DB.
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
