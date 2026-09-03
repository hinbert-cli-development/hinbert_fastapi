"""SMTP email boundary with no credential or token logging."""

import smtplib
from email.message import EmailMessage

from app.core.config.settings import get_settings
from app.models.domain.user import User


def send_email(recipient: str, subject: str, body: str) -> None:
    """Send a plain-text email through configured SMTP; replace with a provider SDK as needed."""
    settings = get_settings()
    if settings.environment == "development" and not settings.smtp_username:
        return
    message = EmailMessage()
    message["From"], message["To"], message["Subject"] = settings.smtp_from, recipient, subject
    message.set_content(body)
    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as smtp:
        smtp.starttls()
        if settings.smtp_username:
            smtp.login(settings.smtp_username, settings.smtp_password.get_secret_value())
        smtp.send_message(message)


def send_verification_email(user: User, token: str) -> None:
    """Send a verification link containing the one-time raw token."""
    send_email(str(user.email), "Verify your email", f"Use this verification token: {token}")


def send_reset_email(user: User, token: str) -> None:
    """Send a password-reset link containing the one-time raw token."""
    send_email(str(user.email), "Reset your password", f"Use this password reset token: {token}")
