"""
FamilyMember model — manage health profiles for a patient's family members.
No external provider needed; stored in the DB and surfaced in-app.
"""

import uuid
from datetime import date, datetime, timezone

from sqlalchemy import Date, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class FamilyMember(Base):
    """A family member's basic health profile, owned by a patient account."""

    __tablename__ = "family_members"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    # The account that owns/manages this family profile
    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    # mother | father | spouse | son | daughter | sibling | guardian | other
    relationship: Mapped[str] = mapped_column(String(30), default="other")
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    gender: Mapped[str | None] = mapped_column(String(20), nullable=True)
    blood_group: Mapped[str | None] = mapped_column(String(5), nullable=True)
    allergies: Mapped[str | None] = mapped_column(Text, nullable=True)
    conditions: Mapped[str | None] = mapped_column(Text, nullable=True)
    emergency_contact: Mapped[str | None] = mapped_column(String(30), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
