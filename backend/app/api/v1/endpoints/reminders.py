"""
Reminder endpoints — in-app medicine / appointment / follow-up reminders.
No external provider needed; reminders are stored in the DB and surfaced in-app.
"""

from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user_id
from app.models.reminder import Reminder
from app.models.user import User
from app.schemas.reminder import (
    ReminderCreate,
    ReminderListResponse,
    ReminderResponse,
    ReminderUpdate,
)
from app.services.email import send_email

router = APIRouter(prefix="/reminders", tags=["Reminders"])


@router.post("/", response_model=ReminderResponse, status_code=status.HTTP_201_CREATED)
async def create_reminder(
    payload: ReminderCreate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Create a new in-app reminder."""
    reminder = Reminder(
        patient_id=UUID(user_id),
        reminder_type=payload.reminder_type,
        title=payload.title,
        notes=payload.notes,
        due_at=payload.due_at,
        recurrence=payload.recurrence,
    )
    db.add(reminder)
    await db.flush()
    await db.refresh(reminder)

    # Best-effort email confirmation (no-op if SMTP not configured).
    user = (
        await db.execute(select(User).where(User.id == UUID(user_id)))
    ).scalar_one_or_none()
    if user and getattr(user, "email", None):
        send_email(
            to=user.email,
            subject=f"LIFELINK Reminder set: {reminder.title}",
            body=(
                f"Hi,\n\nYour {reminder.reminder_type} reminder '{reminder.title}' is set for "
                f"{reminder.due_at:%d %b %Y %H:%M}.\n"
                + (f"Notes: {reminder.notes}\n" if reminder.notes else "")
                + "\n— Project LIFELINK"
            ),
        )
    return reminder


@router.get("/", response_model=ReminderListResponse)
async def list_reminders(
    upcoming_only: bool = Query(default=False),
    include_done: bool = Query(default=True),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """List the current user's reminders (newest due first)."""
    query = select(Reminder).where(
        Reminder.patient_id == UUID(user_id),
        Reminder.is_active == True,  # noqa: E712
    )
    if upcoming_only:
        query = query.where(Reminder.due_at >= datetime.now(timezone.utc))
    if not include_done:
        query = query.where(Reminder.is_done == False)  # noqa: E712

    query = query.order_by(Reminder.due_at.asc())
    result = await db.execute(query)
    reminders = result.scalars().all()
    return ReminderListResponse(
        reminders=[ReminderResponse.model_validate(r) for r in reminders],
        total=len(reminders),
    )


async def _get_owned(document_id: UUID, user_id: str, db: AsyncSession) -> Reminder:
    result = await db.execute(
        select(Reminder).where(
            Reminder.id == document_id,
            Reminder.patient_id == UUID(user_id),
        )
    )
    reminder = result.scalar_one_or_none()
    if not reminder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Reminder not found."
        )
    return reminder


@router.patch("/{reminder_id}", response_model=ReminderResponse)
async def update_reminder(
    reminder_id: UUID,
    payload: ReminderUpdate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Update a reminder (edit fields, mark done, or deactivate)."""
    reminder = await _get_owned(reminder_id, user_id, db)
    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(reminder, field, value)
    await db.flush()
    await db.refresh(reminder)
    return reminder


@router.post("/{reminder_id}/done", response_model=ReminderResponse)
async def mark_done(
    reminder_id: UUID,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Mark a reminder as done. If recurring, roll it to the next occurrence."""
    reminder = await _get_owned(reminder_id, user_id, db)

    next_due = _next_occurrence(reminder.due_at, reminder.recurrence)
    if next_due is not None:
        reminder.due_at = next_due
        reminder.is_done = False
    else:
        reminder.is_done = True

    await db.flush()
    await db.refresh(reminder)
    return reminder


@router.delete("/{reminder_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_reminder(
    reminder_id: UUID,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Delete a reminder."""
    reminder = await _get_owned(reminder_id, user_id, db)
    await db.delete(reminder)


def _next_occurrence(current: datetime, recurrence: str) -> datetime | None:
    """Compute the next due date for a recurring reminder, or None if one-off."""
    from datetime import timedelta

    if recurrence == "daily":
        return current + timedelta(days=1)
    if recurrence == "weekly":
        return current + timedelta(weeks=1)
    if recurrence == "monthly":
        # Approx month as 30 days (keeps it dependency-free).
        return current + timedelta(days=30)
    return None
