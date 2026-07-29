"""
Document Embedding model — stores vector embeddings for RAG (AI search).
Uses pgvector for similarity search.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base

# Note: pgvector column type will be added after pgvector SQLAlchemy extension is imported
# For now, we store embedding as a reference — actual vector column added in migration


class DocumentEmbedding(Base):
    """A chunk of text from a document with its vector embedding for AI search."""

    __tablename__ = "document_embeddings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("medical_documents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # Chunk info
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)  # Order in document
    chunk_text: Mapped[str] = mapped_column(Text, nullable=False)  # The actual text chunk
    # embedding: vector(768) — added via raw SQL in migration (pgvector type)
    # Metadata
    page_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    section_title: Mapped[str | None] = mapped_column(String(500), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
