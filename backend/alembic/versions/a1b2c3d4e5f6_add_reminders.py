"""add reminders table

Revision ID: a1b2c3d4e5f6
Revises: 398851c6a6e5
Create Date: 2026-10-27 00:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "398851c6a6e5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "reminders",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("patient_id", sa.UUID(), nullable=False),
        sa.Column("reminder_type", sa.String(length=30), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("recurrence", sa.String(length=20), nullable=False),
        sa.Column("is_done", sa.Boolean(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["patient_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_reminders_patient_id"), "reminders", ["patient_id"], unique=False
    )
    op.create_index(op.f("ix_reminders_due_at"), "reminders", ["due_at"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_reminders_due_at"), table_name="reminders")
    op.drop_index(op.f("ix_reminders_patient_id"), table_name="reminders")
    op.drop_table("reminders")
