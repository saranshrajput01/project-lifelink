"""
Medical Document model — tracks uploaded files and their processing status.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class MedicalDocument(Base):
    """A medical document uploaded by a patient (prescription, lab report, etc.)."""

    __tablename__ = "medical_documents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    # Document info
    doc_type: Mapped[str] = mapped_column(
        String(50),
        default="unknown",
        # prescription | lab_report | discharge_summary | doctor_notes | vaccination | insurance | other
    )
    original_filename: Mapped[str] = mapped_column(String(500), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    s3_key: Mapped[str] = mapped_column(
        String(1000), nullable=False
    )  # Path in S3/MinIO

    # Processing status
    ocr_status: Mapped[str] = mapped_column(
        String(20), default="pending"  # pending | processing | completed | failed
    )
    processing_status: Mapped[str] = mapped_column(
        String(20), default="pending"  # pending | processing | completed | failed
    )

    # Extracted data (filled after AI processing)
    raw_text: Mapped[str | None] = mapped_column(Text, nullable=True)  # OCR output
    extracted_data: Mapped[dict | None] = mapped_column(
        JSONB, nullable=True
    )  # Structured extraction
    summary_short: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )  # 1-line summary
    summary_detailed: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )  # Full summary
    ai_confidence: Mapped[float | None] = mapped_column(nullable=True)  # 0.0 to 1.0

    # Metadata
    document_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    doctor_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    hospital_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    tags: Mapped[list | None] = mapped_column(
        JSONB, nullable=True
    )  # ["blood_test", "routine"]

    # Timestamps
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    processed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
