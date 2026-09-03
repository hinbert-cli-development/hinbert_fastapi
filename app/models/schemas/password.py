"""Password recovery payloads."""

from pydantic import BaseModel, EmailStr, Field


class ForgotPassword(BaseModel):
    """Email address used to request a reset link."""

    email: EmailStr


class ResetPassword(BaseModel):
    """Single-use reset token and replacement password."""

    token: str
    password: str = Field(min_length=12, max_length=72)
