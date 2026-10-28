"""
Email service — send notifications via SMTP (e.g. Gmail app password).

Degrades gracefully: if SMTP isn't configured, send_email() returns False
instead of raising, so callers can treat email as best-effort.
"""

import logging
import smtplib
from email.message import EmailMessage

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def send_email(to: str, subject: str, body: str, html: str | None = None) -> bool:
    """Send a plaintext (optionally HTML) email. Returns True on success."""
    if not settings.email_enabled:
        logger.info("[email] SMTP not configured — skipping email to %s", to)
        return False

    msg = EmailMessage()
    msg["From"] = settings.SMTP_FROM
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)
    if html:
        msg.add_alternative(html, subtype="html")

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASS)
            server.send_message(msg)
        logger.info("[email] sent to %s: %s", to, subject)
        return True
    except Exception as e:
        logger.error("[email] failed to send to %s: %s", to, e)
        return False
