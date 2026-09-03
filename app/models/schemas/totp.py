"""Two-factor setup and verification payloads."""

from pydantic import BaseModel, Field


class TotpVerify(BaseModel):
    """Six-digit current TOTP code."""

    code: str = Field(pattern=r"^\d{6}$")
