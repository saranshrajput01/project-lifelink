"""
RAG service — build and query the pgvector index over a user's document chunks.

- index_document: chunk a document's text, embed it, and (re)write its rows
  into document_embeddings.
- retrieve: given a user's query, return the most relevant chunks across all
  of that user's documents using pgvector cosine distance.

All functions degrade gracefully if the embedding model is unavailable.
"""

import logging
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.embedding import DocumentEmbedding
from app.services.embeddings import chunk_text, embed_query, embed_texts, is_available

logger = logging.getLogger(__name__)


async def index_document(
    db: AsyncSession,
    *,
    document_id: UUID,
    patient_id: UUID,
    text: str,
) -> int:
    """Chunk + embed a document's text and replace its embedding rows.

    Returns the number of chunks indexed (0 if skipped/unavailable).
    """
    if not text or not is_available():
        return 0

    chunks = chunk_text(text)
    if not chunks:
        return 0

    vectors = await embed_texts(chunks)
    if not vectors:
        return 0

    # Replace any existing embeddings for this document (idempotent reprocess).
    await db.execute(
        delete(DocumentEmbedding).where(DocumentEmbedding.document_id == document_id)
    )

    for idx, (chunk, vec) in enumerate(zip(chunks, vectors)):
        db.add(
            DocumentEmbedding(
                document_id=document_id,
                patient_id=patient_id,
                chunk_index=idx,
                chunk_text=chunk,
                embedding=vec,
            )
        )
    await db.flush()
    logger.info("[RAG] Indexed %d chunks for document %s", len(chunks), document_id)
    return len(chunks)


async def retrieve(
    db: AsyncSession,
    *,
    patient_id: UUID,
    query: str,
    top_k: int = 5,
) -> list[str]:
    """Return the top-k most relevant chunk texts for a user's query.

    Empty list if embeddings are unavailable or the user has no indexed chunks.
    """
    if not query or not is_available():
        return []

    qvec = await embed_query(query)
    if qvec is None:
        return []

    stmt = (
        select(DocumentEmbedding.chunk_text)
        .where(
            DocumentEmbedding.patient_id == patient_id,
            DocumentEmbedding.embedding.isnot(None),
        )
        .order_by(DocumentEmbedding.embedding.cosine_distance(qvec))
        .limit(top_k)
    )
    result = await db.execute(stmt)
    return [row[0] for row in result.all()]
