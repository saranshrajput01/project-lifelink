"""
FamilyMember schemas — request/response models for family health profiles.
"""

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field


class FamilyMemberCreate(BaseModel):
    """Payload to create a family member profile."""

    full_name: str = Field(..., min_length=1, max_length=255)
    relationship: str = Field(default="other")
    date_of_birth: date | None = None
    gender: str | None = None
    blood_group: str | None = Field(default=None, max_length=5)
    allergies: str | None = None
    conditions: str | None = None
    emergency_contact: str | None = None
    notes: str | None = None


class FamilyMemberUpdate(BaseModel):
    """Partial update for a family member profile."""

    full_name: str | None = Field(default=None, min_length=1, max_length=255)
    relationship: str | None = None
    date_of_birth: date | None = None
    gender: str | None = None
    blood_group: str | None = Field(default=None, max_length=5)
    allergies: str | None = None
    conditions: str | None = None
    emergency_contact: str | None = None
    notes: str | None = None


class FamilyMemberResponse(BaseModel):
    """Response model for a family member profile."""

    id: UUID
    owner_id: UUID
    full_name: str
    relationship: str
    date_of_birth: date | None = None
    gender: str | None = None
    blood_group: str | None = None
    allergies: str | None = None
    conditions: str | None = None
    emergency_contact: str | None = None
    notes: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class FamilyMemberListResponse(BaseModel):
    """List of family member profiles."""

    members: list[FamilyMemberResponse]
    total: int
