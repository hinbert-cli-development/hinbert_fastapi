"""User input/output schemas that exclude password hashes."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    """Validated signup payload."""

    email: EmailStr
    full_name: str = Field(min_length=1, max_length=200)
    password: str = Field(min_length=12, max_length=128)


class UserUpdate(BaseModel):
    """Partial profile update payload."""

    full_name: str | None = Field(default=None, min_length=1, max_length=200)


class AdminUserUpdate(UserUpdate):
    """Administrator-only profile and role update payload."""

    is_active: bool | None = None
    is_admin: bool | None = None


class UserOut(BaseModel):
    """Safe public user representation."""

    model_config = ConfigDict(from_attributes=True)
    id: UUID
    email: EmailStr
    full_name: str
    is_active: bool
    is_verified: bool
