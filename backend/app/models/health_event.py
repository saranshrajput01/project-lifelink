"""
Health Event model — represents events in a patient's health timeline.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class HealthEvent(Base):
    """A single event in patient's health timeline (visit, diagnosis, procedure, etc.)."""

    __tablename__ = "health_events"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    # Link to source document (optional — some events are manually added)
    document_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("medical_documents.id", ondelete="SET NULL"),
        nullable=True,
    )
    # Event details
    event_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        # doctor_visit | lab_test | diagnosis | medication_start | medication_stop
        # procedure | surgery | hospitalization | vaccination | checkup
    )
    event_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    severity: Mapped[str] = mapped_column(
        String(20), default="normal"  # normal | attention | warning | critical
    )
    metadata_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    # e.g., {"doctor": "Dr. Sharma", "hospital": "AIIMS", "icd_code": "E11.9"}

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
