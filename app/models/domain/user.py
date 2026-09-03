"""User table storing identity, authorization, and password state."""

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.domain.base import TimestampedModel

if TYPE_CHECKING:
    from app.models.domain.email_verification import EmailVerification
    from app.models.domain.password_reset import PasswordReset
    from app.models.domain.refresh_token import RefreshToken
    from app.models.domain.totp_secret import TotpSecret


class User(TimestampedModel):
    """Application user; email is unique and password hashes are never exposed."""

    __tablename__ = "users"
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(200))
    password_hash: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    email_verifications: Mapped[list["EmailVerification"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    password_resets: Mapped[list["PasswordReset"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    totp_secret: Mapped["TotpSecret | None"] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
