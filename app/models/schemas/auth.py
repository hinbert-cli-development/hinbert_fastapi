"""Authentication request schemas."""

from pydantic import BaseModel, EmailStr, Field


class SignupRequest(BaseModel):
    """Signup data with a deliberately strong minimum password length."""

    email: EmailStr
    full_name: str = Field(min_length=1, max_length=200)
    password: str = Field(min_length=12, max_length=72)


class LoginRequest(BaseModel):
    """Credential login payload."""

    email: EmailStr
    password: str


class EmailTokenRequest(BaseModel):
    """Single-use email verification token payload."""

    token: str = Field(min_length=20)


class SocialAuthRequest(BaseModel):
    """OAuth callback data returned by a supported provider."""

    code: str = Field(min_length=1)
