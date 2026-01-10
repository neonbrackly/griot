"""Configuration settings for griot-registry."""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_prefix="GRIOT_REGISTRY_",
        env_file=".env",
        extra="ignore",
    )

    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"

    # API settings
    api_v1_prefix: str = "/api/v1"
    cors_origins: list[str] = ["*"]

    # Storage settings
    storage_backend: Literal["filesystem", "git", "postgres"] = "filesystem"
    storage_path: str = "./data/contracts"

    # PostgreSQL settings (when storage_backend="postgres")
    postgres_dsn: str | None = None

    # Git settings (when storage_backend="git")
    git_repo_path: str | None = None
    git_branch: str = "main"

    # Auth settings
    auth_enabled: bool = False
    api_key_header: str = "X-API-Key"
    api_keys: list[str] = []


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
