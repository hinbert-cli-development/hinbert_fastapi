"""Validated environment configuration for every runtime component.

Pydantic Settings reads environment variables and an optional ``.env`` file,
making deployments twelve-factor friendly. Change defaults here only for safe
local development; production secrets must come from a secret manager.
"""

from functools import lru_cache

from pydantic import AliasChoices, Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with validation and conservative security defaults."""

    app_name: str = "Hinbert FastAPI"
    api_prefix: str = "/api/v1"
    environment: str = "development"
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/app",
        validation_alias=AliasChoices("DATABASE_URL", "HINBERT_DATABASE_URL"),
    )
    redis_url: str = "redis://localhost:6379/0"
    jwt_secret_key: SecretStr = Field(
        default=SecretStr("change-me-in-production"),
        validation_alias=AliasChoices("SECRET_KEY", "HINBERT_JWT_SECRET_KEY"),
    )
    jwt_algorithm: str = Field(default="HS256", validation_alias=AliasChoices("ALGORITHM", "HINBERT_JWT_ALGORITHM"))
    access_token_minutes: int = Field(
        default=15, validation_alias=AliasChoices("ACCESS_TOKEN_EXPIRE_MINUTES", "HINBERT_ACCESS_TOKEN_MINUTES")
    )
    refresh_token_days: int = Field(
        default=30, validation_alias=AliasChoices("REFRESH_TOKEN_EXPIRE_DAYS", "HINBERT_REFRESH_TOKEN_DAYS")
    )
    cors_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:3000"],
        validation_alias=AliasChoices("BACKEND_CORS_ORIGINS", "HINBERT_CORS_ORIGINS"),
    )
    smtp_host: str = Field(default="localhost", validation_alias=AliasChoices("SMTP_HOST", "HINBERT_SMTP_HOST"))
    smtp_port: int = Field(default=587, validation_alias=AliasChoices("SMTP_PORT", "HINBERT_SMTP_PORT"))
    smtp_username: str = Field(default="", validation_alias=AliasChoices("SMTP_USER", "HINBERT_SMTP_USERNAME"))
    smtp_password: SecretStr = Field(
        default=SecretStr(""), validation_alias=AliasChoices("SMTP_PASSWORD", "HINBERT_SMTP_PASSWORD")
    )
    smtp_from: str = Field(
        default="no-reply@example.com", validation_alias=AliasChoices("EMAIL_FROM", "HINBERT_SMTP_FROM")
    )
    google_client_id: str = Field(
        default="", validation_alias=AliasChoices("GOOGLE_CLIENT_ID", "HINBERT_GOOGLE_CLIENT_ID")
    )
    google_client_secret: SecretStr = Field(
        default=SecretStr(""), validation_alias=AliasChoices("GOOGLE_CLIENT_SECRET", "HINBERT_GOOGLE_CLIENT_SECRET")
    )
    facebook_client_id: str = Field(
        default="", validation_alias=AliasChoices("FACEBOOK_CLIENT_ID", "HINBERT_FACEBOOK_CLIENT_ID")
    )
    facebook_client_secret: SecretStr = Field(
        default=SecretStr(""), validation_alias=AliasChoices("FACEBOOK_CLIENT_SECRET", "HINBERT_FACEBOOK_CLIENT_SECRET")
    )
    rate_limit: str = Field(
        default="100/minute", validation_alias=AliasChoices("RATE_LIMIT_PER_MINUTE", "HINBERT_RATE_LIMIT")
    )

    model_config = SettingsConfigDict(env_file=".env", env_prefix="", extra="ignore")

    @field_validator("jwt_secret_key")
    @classmethod
    def reject_weak_production_secret(cls, value: SecretStr) -> SecretStr:
        """Prevent the documented development secret from reaching production."""
        secret = value.get_secret_value()
        if secret == "change-me-in-production" or len(secret) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters and must not use the default value")
        return value


@lru_cache
def get_settings() -> Settings:
    """Return one cached, validated settings object per process."""
    return Settings()
