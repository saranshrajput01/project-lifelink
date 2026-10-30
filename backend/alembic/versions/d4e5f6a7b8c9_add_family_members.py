"""add family_members table

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-10-30
"""

from typing import Sequence, Union

from alembic import op

revision: str = "d4e5f6a7b8c9"
down_revision: Union[str, None] = "c3d4e5f6a7b8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # IF NOT EXISTS: local DBs already have this table (created outside alembic).
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS family_members (
            id UUID PRIMARY KEY,
            owner_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            full_name VARCHAR(255) NOT NULL,
            relationship VARCHAR(30),
            date_of_birth DATE,
            gender VARCHAR(20),
            blood_group VARCHAR(5),
            allergies TEXT,
            conditions TEXT,
            emergency_contact VARCHAR(30),
            notes TEXT,
            created_at TIMESTAMPTZ,
            updated_at TIMESTAMPTZ
        )
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_family_members_owner_id "
        "ON family_members (owner_id)"
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS family_members")
