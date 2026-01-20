"""Configuration settings for griot-registry.

Settings are loaded from environment variables with the GRIOT_REGISTRY_ prefix.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_prefix="GRIOT_REGISTRY_",
        env_file=".env",
        extra="ignore",
    )

    # ==========================================================================
    # Server Settings
    # ==========================================================================
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"

    # ==========================================================================
    # API Settings
    # ==========================================================================
    api_v1_prefix: str = "/api/v1"
    cors_origins: list[str] = ["*"]

    # ==========================================================================
    # Storage Settings (MongoDB)
    # ==========================================================================
    storage_backend: Literal["mongodb"] = "mongodb"
    mongodb_uri: str = Field(
        default="mongodb://localhost:27017",
        description="MongoDB connection URI",
    )
    mongodb_database: str = Field(
        default="griot_registry",
        description="MongoDB database name",
    )

    # ==========================================================================
    # Authentication Settings
    # ==========================================================================
    auth_enabled: bool = Field(
        default=True,
        description="Enable authentication (disable only for local development)",
    )

    # API Key Authentication
    api_key_header: str = "X-API-Key"
    api_keys: list[str] = Field(
        default_factory=list,
        description="List of valid API keys (for service-to-service auth)",
    )

    # JWT Authentication
    jwt_secret_key: SecretStr = Field(
        default=SecretStr("change-me-in-production-use-a-strong-secret"),
        description="Secret key for JWT signing (use a strong random value in production)",
    )
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = Field(
        default=60,
        description="Access token expiration time in minutes",
    )
    jwt_refresh_token_expire_days: int = Field(
        default=7,
        description="Refresh token expiration time in days",
    )
    jwt_issuer: str = Field(
        default="griot-registry",
        description="JWT issuer claim",
    )

    # OAuth2/OIDC (optional, for enterprise SSO)
    oauth_enabled: bool = False
    oauth_provider_url: str | None = None
    oauth_client_id: str | None = None
    oauth_client_secret: SecretStr | None = None
    oauth_audience: str | None = None

    # ==========================================================================
    # Contract Validation Settings
    # ==========================================================================
    validate_on_create: bool = Field(
        default=True,
        description="Run linting/validation when creating contracts",
    )
    validate_on_update: bool = Field(
        default=True,
        description="Run linting/validation when updating contracts",
    )
    block_on_lint_errors: bool = Field(
        default=True,
        description="Block contract creation/update if lint errors are found",
    )
    block_on_lint_warnings: bool = Field(
        default=False,
        description="Block contract creation/update if lint warnings are found",
    )


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
