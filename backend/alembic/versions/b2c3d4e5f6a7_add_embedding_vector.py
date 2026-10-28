"""add embedding vector column to document_embeddings

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-10-27 00:05:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector

# revision identifiers
revision: str = "b2c3d4e5f6a7"
down_revision: Union[str, None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

EMBEDDING_DIM = 384


def upgrade() -> None:
    # Ensure pgvector extension exists (image is pgvector/pgvector:pg16).
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.add_column(
        "document_embeddings",
        sa.Column("embedding", Vector(EMBEDDING_DIM), nullable=True),
    )
    # Approximate-NN index for fast cosine similarity search.
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_document_embeddings_embedding "
        "ON document_embeddings USING ivfflat (embedding vector_cosine_ops) "
        "WITH (lists = 100)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_document_embeddings_embedding")
    op.drop_column("document_embeddings", "embedding")
