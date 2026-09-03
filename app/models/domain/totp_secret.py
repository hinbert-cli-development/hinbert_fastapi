"""Encrypted-at-rest TOTP secret ownership boundary."""

from uuid import UUID

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class TotpSecret(Base):
    """One TOTP secret per user; production deployments should encrypt its value."""

    __tablename__ = "totp_secrets"
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    secret: Mapped[str] = mapped_column(String(128))
