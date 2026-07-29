"""
Risk Assessment model — stores ML model predictions for disease risks.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class RiskAssessment(Base):
    """AI-predicted disease risk score for a patient."""

    __tablename__ = "risk_assessments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # Risk details
    disease_type: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
        # cardiovascular | diabetes | chronic_kidney_disease | readmission
    )
    risk_score: Mapped[float] = mapped_column(Float, nullable=False)  # 0.0 to 1.0 probability
    risk_level: Mapped[str] = mapped_column(
        String(20), nullable=False  # low | moderate | high | critical
    )
    # Explainability
    contributing_factors: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    # [{"factor": "high_cholesterol", "impact": 0.3, "direction": "increases_risk"}]
    recommendations: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    # ["Reduce salt intake", "Exercise 30min daily", "Follow up with cardiologist"]
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Natural language explanation of why this risk score

    # Model info
    model_version: Mapped[str] = mapped_column(String(50), nullable=False)
    model_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)

    assessed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
