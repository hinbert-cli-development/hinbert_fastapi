"""SMTP email boundary with no credential or token logging."""

import smtplib
from email.message import EmailMessage

from app.core.config.settings import get_settings


def send_email(recipient: str, subject: str, body: str) -> None:
    """Send a plain-text email through configured SMTP; replace with a provider SDK as needed."""
    settings = get_settings()
    message = EmailMessage()
    message["From"], message["To"], message["Subject"] = settings.smtp_from, recipient, subject
    message.set_content(body)
    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as smtp:
        smtp.starttls()
        if settings.smtp_username:
            smtp.login(settings.smtp_username, settings.smtp_password.get_secret_value())
        smtp.send_message(message)
