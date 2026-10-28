"""
Health Metric model — tracks lab values and vitals over time (for trend charts).
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class HealthMetric(Base):
    """A single health measurement (blood sugar, BP, cholesterol, etc.)."""

    __tablename__ = "health_metrics"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    document_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("medical_documents.id", ondelete="SET NULL"),
        nullable=True,
    )
    # Metric details
    metric_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        # blood_sugar_fasting | blood_sugar_pp | hba1c | hemoglobin
        # cholesterol_total | cholesterol_hdl | cholesterol_ldl
        # bp_systolic | bp_diastolic | creatinine | bun | egfr
        # tsh | t3 | t4 | alt | ast | bilirubin | uric_acid
    )
    value: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(
        String(30), nullable=False
    )  # mg/dL, g/dL, mmHg, etc.
    reference_min: Mapped[float | None] = mapped_column(Float, nullable=True)
    reference_max: Mapped[float | None] = mapped_column(Float, nullable=True)
    flag: Mapped[str | None] = mapped_column(
        String(10), nullable=True  # LOW | HIGH | NORMAL | CRITICAL
    )
    source: Mapped[str] = mapped_column(
        String(30), default="document"  # document | manual | wearable
    )
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
