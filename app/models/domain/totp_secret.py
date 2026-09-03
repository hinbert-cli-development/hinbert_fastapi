"""Encrypted-at-rest TOTP secret ownership boundary."""

from typing import TYPE_CHECKING
from uuid import UUID

from cryptography.fernet import Fernet, InvalidToken
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.config.settings import get_settings
from app.db.base import Base

if TYPE_CHECKING:
    from app.models.domain.user import User


class TotpSecret(Base):
    """One TOTP secret per user; production deployments should encrypt its value."""

    __tablename__ = "totp_secrets"
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    encrypted_secret: Mapped[str] = mapped_column(String(512))
    user: Mapped["User"] = relationship(back_populates="totp_secret")

    @property
    def secret(self) -> str:
        """Decrypt the secret only at the point where TOTP verification needs it."""
        try:
            return Fernet(_fernet_key()).decrypt(self.encrypted_secret.encode()).decode()
        except InvalidToken as exc:
            raise ValueError("Stored TOTP secret cannot be decrypted") from exc

    @secret.setter
    def secret(self, value: str) -> None:
        """Encrypt a plaintext secret before SQLAlchemy persists it."""
        self.encrypted_secret = Fernet(_fernet_key()).encrypt(value.encode()).decode()


def _fernet_key() -> bytes:
    """Return a Fernet key derived from the configured secret key."""
    import base64
    import hashlib

    return base64.urlsafe_b64encode(hashlib.sha256(get_settings().jwt_secret_key.get_secret_value().encode()).digest())
