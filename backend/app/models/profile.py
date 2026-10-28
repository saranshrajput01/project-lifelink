"""
User Profile model — stores patient health profile details.
"""

import uuid
from datetime import date, datetime, timezone

from sqlalchemy import Date, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class UserProfile(Base):
    """Extended user profile — health-specific information."""

    __tablename__ = "user_profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    gender: Mapped[str | None] = mapped_column(
        String(20), nullable=True
    )  # male | female | other
    blood_group: Mapped[str | None] = mapped_column(
        String(5), nullable=True
    )  # A+, B-, O+, AB+ etc.
    height_cm: Mapped[float | None] = mapped_column(nullable=True)
    weight_kg: Mapped[float | None] = mapped_column(nullable=True)
    allergies: Mapped[list | None] = mapped_column(
        JSONB, nullable=True
    )  # ["Penicillin", "Dust"]
    chronic_conditions: Mapped[list | None] = mapped_column(
        JSONB, nullable=True
    )  # ["Diabetes", "Hypertension"]
    emergency_contact_name: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )
    emergency_contact_phone: Mapped[str | None] = mapped_column(
        String(20), nullable=True
    )
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
