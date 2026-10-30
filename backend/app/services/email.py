"""
Email service.

Two transports, tried in this order:
1. Brevo HTTPS API (BREVO_API_KEY) — works on Render's free tier, which blocks
   outbound SMTP ports 25/465/587.
2. SMTP (e.g. Gmail app password) — works locally / on paid hosts.

Degrades gracefully: if nothing is configured, send_email() returns False
instead of raising, so callers can treat email as best-effort.
"""

import json
import logging
import smtplib
import urllib.error
import urllib.request
from email.message import EmailMessage
from email.utils import parseaddr

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

BREVO_URL = "https://api.brevo.com/v3/smtp/email"


def _send_brevo(to: str, subject: str, body: str, html: str | None) -> bool:
    name, addr = parseaddr(settings.SMTP_FROM)
    sender = {"email": settings.BREVO_SENDER_EMAIL or addr}
    if name:
        sender["name"] = name
    payload = {
        "sender": sender,
        "to": [{"email": to}],
        "subject": subject,
        "textContent": body,
    }
    if html:
        payload["htmlContent"] = html
    req = urllib.request.Request(
        BREVO_URL,
        data=json.dumps(payload).encode(),
        headers={
            "api-key": settings.BREVO_API_KEY,
            "content-type": "application/json",
            "accept": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            ok = 200 <= resp.status < 300
        logger.info("[email] brevo sent to %s: %s", to, subject)
        return ok
    except urllib.error.HTTPError as e:
        logger.error(
            "[email] brevo failed for %s: %s %s",
            to,
            e.code,
            e.read().decode(errors="replace")[:300],
        )
    except Exception as e:
        logger.error("[email] brevo failed for %s: %s", to, e)
    return False


def _send_smtp(to: str, subject: str, body: str, html: str | None) -> bool:
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
        logger.info("[email] smtp sent to %s: %s", to, subject)
        return True
    except Exception as e:
        logger.error("[email] smtp failed to send to %s: %s", to, e)
        return False


def send_email(to: str, subject: str, body: str, html: str | None = None) -> bool:
    """Send a plaintext (optionally HTML) email. Returns True on success."""
    if settings.BREVO_API_KEY:
        return _send_brevo(to, subject, body, html)
    if settings.SMTP_HOST and settings.SMTP_USER and settings.SMTP_PASS:
        return _send_smtp(to, subject, body, html)
    logger.info("[email] no email transport configured — skipping email to %s", to)
    return False
