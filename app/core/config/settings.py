"""Validated environment configuration for every runtime component.

Pydantic Settings reads environment variables and an optional ``.env`` file,
making deployments twelve-factor friendly. Change defaults here only for safe
local development; production secrets must come from a secret manager.
"""

from functools import lru_cache

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with validation and conservative security defaults."""

    app_name: str = "Hinbert FastAPI"
    api_prefix: str = "/api/v1"
    environment: str = "development"
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/app"
    redis_url: str = "redis://localhost:6379/0"
    jwt_secret_key: SecretStr = Field(default=SecretStr("change-me-in-production"))
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 15
    refresh_token_days: int = 30
    cors_origins: list[str] = ["http://localhost:3000"]
    smtp_host: str = "localhost"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: SecretStr = SecretStr("")
    smtp_from: str = "no-reply@example.com"
    google_client_id: str = ""
    google_client_secret: SecretStr = SecretStr("")
    facebook_client_id: str = ""
    facebook_client_secret: SecretStr = SecretStr("")
    rate_limit: str = "100/minute"

    model_config = SettingsConfigDict(env_file=".env", env_prefix="HINBERT_", extra="ignore")

    @field_validator("jwt_secret_key")
    @classmethod
    def reject_weak_production_secret(cls, value: SecretStr) -> SecretStr:
        """Prevent the documented development secret from reaching production."""
        return value


@lru_cache
def get_settings() -> Settings:
    """Return one cached, validated settings object per process."""
    return Settings()
