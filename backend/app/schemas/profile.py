"""
Profile schemas — request/response models for user profile endpoints.
"""

from datetime import date
from uuid import UUID

from pydantic import BaseModel, Field


class ProfileUpdate(BaseModel):
    """Request body for creating/updating a user profile."""

    date_of_birth: date | None = None
    gender: str | None = Field(None, pattern="^(male|female|other)$")
    blood_group: str | None = Field(None, pattern="^(A|B|AB|O)[+-]$")
    height_cm: float | None = Field(None, gt=0, lt=300)
    weight_kg: float | None = Field(None, gt=0, lt=500)
    allergies: list[str] | None = None
    chronic_conditions: list[str] | None = None
    emergency_contact_name: str | None = None
    emergency_contact_phone: str | None = None
    address: str | None = None


class ProfileResponse(BaseModel):
    """Response model for user profile."""

    id: UUID
    user_id: UUID
    date_of_birth: date | None = None
    gender: str | None = None
    blood_group: str | None = None
    height_cm: float | None = None
    weight_kg: float | None = None
    allergies: list[str] | None = None
    chronic_conditions: list[str] | None = None
    emergency_contact_name: str | None = None
    emergency_contact_phone: str | None = None
    address: str | None = None

    model_config = {"from_attributes": True}
