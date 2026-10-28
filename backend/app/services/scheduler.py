"""
Reminder notification scheduler — dependency-free asyncio background loop.

Started on FastAPI startup. Every CHECK_INTERVAL seconds it looks for reminders
whose due time has arrived and that haven't been notified yet, emails the user,
marks them notified, and rolls recurring reminders to their next occurrence.

No external scheduler (Celery/APScheduler) needed — fine for a single instance.
"""

import asyncio
import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from app.core.database import async_session_factory
from app.models.reminder import Reminder
from app.models.user import User
from app.services.email import send_email

logger = logging.getLogger(__name__)

CHECK_INTERVAL = 60  # seconds
_task: asyncio.Task | None = None


def _next_occurrence(current: datetime, recurrence: str) -> datetime | None:
    if recurrence == "daily":
        return current + timedelta(days=1)
    if recurrence == "weekly":
        return current + timedelta(weeks=1)
    if recurrence == "monthly":
        return current + timedelta(days=30)
    return None


async def _process_due_reminders() -> int:
    """Email every due, un-notified, active reminder. Returns count notified."""
    now = datetime.now(timezone.utc)
    notified = 0
    async with async_session_factory() as db:
        rows = (
            (
                await db.execute(
                    select(Reminder).where(
                        Reminder.is_active == True,  # noqa: E712
                        Reminder.is_done == False,  # noqa: E712
                        Reminder.notified == False,  # noqa: E712
                        Reminder.due_at <= now,
                    )
                )
            )
            .scalars()
            .all()
        )

        for r in rows:
            user = (
                await db.execute(select(User).where(User.id == r.patient_id))
            ).scalar_one_or_none()
            if user and getattr(user, "email", None):
                send_email(
                    to=user.email,
                    subject=f"⏰ LIFELINK Reminder: {r.title}",
                    body=(
                        f"Hi,\n\nThis is your {r.reminder_type} reminder:\n\n"
                        f"  {r.title}\n"
                        + (f"  Notes: {r.notes}\n" if r.notes else "")
                        + f"  Due: {r.due_at:%d %b %Y %H:%M}\n\n"
                        "Stay healthy,\n— Project LIFELINK"
                    ),
                )
            # Roll recurring; otherwise just mark notified.
            nxt = _next_occurrence(r.due_at, r.recurrence)
            if nxt is not None:
                r.due_at = nxt
                r.notified = False  # will fire again at next occurrence
            else:
                r.notified = True
            notified += 1

        if notified:
            await db.commit()
    return notified


async def _loop():
    logger.info("[scheduler] reminder notifier started (every %ss)", CHECK_INTERVAL)
    while True:
        try:
            n = await _process_due_reminders()
            if n:
                logger.info("[scheduler] notified %d due reminder(s)", n)
        except Exception as e:  # never let the loop die
            logger.error("[scheduler] error: %s", e)
        await asyncio.sleep(CHECK_INTERVAL)


def start_scheduler():
    """Launch the background loop (idempotent)."""
    global _task
    if _task is None or _task.done():
        _task = asyncio.create_task(_loop())


def stop_scheduler():
    global _task
    if _task and not _task.done():
        _task.cancel()
        _task = None
