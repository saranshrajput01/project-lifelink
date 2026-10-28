"""
Reminder schemas — request/response models for in-app reminders.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ReminderCreate(BaseModel):
    """Payload to create a reminder."""

    title: str = Field(..., min_length=1, max_length=255)
    reminder_type: str = Field(default="medication")
    notes: str | None = None
    due_at: datetime
    recurrence: str = Field(default="none")  # none | daily | weekly | monthly


class ReminderUpdate(BaseModel):
    """Partial update for a reminder."""

    title: str | None = Field(default=None, min_length=1, max_length=255)
    reminder_type: str | None = None
    notes: str | None = None
    due_at: datetime | None = None
    recurrence: str | None = None
    is_done: bool | None = None
    is_active: bool | None = None


class ReminderResponse(BaseModel):
    """Response model for a reminder."""

    id: UUID
    patient_id: UUID
    reminder_type: str
    title: str
    notes: str | None = None
    due_at: datetime
    recurrence: str
    is_done: bool
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ReminderListResponse(BaseModel):
    """List of reminders."""

    reminders: list[ReminderResponse]
    total: int
