"""
Embedding service — local sentence-transformers (all-MiniLM-L6-v2, 384-dim).
Used to build and query the pgvector RAG index over a user's document chunks.

The model is heavy-ish and loaded lazily as a singleton. If it can't load
(e.g. not installed in a given environment), callers degrade gracefully.
"""

import asyncio
import logging

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

_model = None
EMBEDDING_DIM = 384


def _get_model():
    """Lazy-load the sentence-transformers model once. Returns None if unavailable."""
    global _model
    if _model is not None:
        return _model
    try:
        from sentence_transformers import SentenceTransformer

        _model = SentenceTransformer(settings.EMBEDDING_MODEL)
        logger.info("[EMB] Loaded embedding model: %s", settings.EMBEDDING_MODEL)
    except Exception as e:
        logger.warning("[EMB] Embedding model unavailable: %s", e)
        _model = None
    return _model


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 120) -> list[str]:
    """Split text into overlapping word-based chunks suitable for embedding."""
    words = (text or "").split()
    if not words:
        return []
    chunks: list[str] = []
    step = max(chunk_size - overlap, 1)
    for start in range(0, len(words), step):
        chunk = " ".join(words[start : start + chunk_size])
        if chunk.strip():
            chunks.append(chunk)
        if start + chunk_size >= len(words):
            break
    return chunks


def _embed_sync(texts: list[str]) -> list[list[float]] | None:
    model = _get_model()
    if model is None or not texts:
        return None
    try:
        vectors = model.encode(texts, normalize_embeddings=True)
        return [v.tolist() for v in vectors]
    except Exception as e:
        logger.error("[EMB] encode failed: %s", e)
        return None


async def embed_texts(texts: list[str]) -> list[list[float]] | None:
    """Embed a list of texts (off the event loop). Returns None if unavailable."""
    return await asyncio.to_thread(_embed_sync, texts)


async def embed_query(text: str) -> list[float] | None:
    """Embed a single query string. Returns None if unavailable."""
    result = await embed_texts([text])
    return result[0] if result else None


def is_available() -> bool:
    """Whether the embedding model can be used."""
    return _get_model() is not None
