"""Application configuration loaded from environment variables."""

from functools import lru_cache
from typing import Literal

from pydantic import AnyHttpUrl, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Validated runtime settings.

    Local defaults match the development Compose stack. Deployments must override the
    database URL with an environment-specific secret.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="OPSPILOT_",
        extra="ignore",
    )

    app_name: str = "OpsPilot"
    environment: Literal["development", "test", "production"] = "development"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    database_url: SecretStr = SecretStr(
        "postgresql+psycopg://opspilot:opspilot@localhost:5432/opspilot"
    )
    qdrant_url: AnyHttpUrl = AnyHttpUrl("http://localhost:6333")
    readiness_timeout_seconds: float = Field(default=2.0, gt=0, le=30)


@lru_cache
def get_settings() -> Settings:
    """Return one validated settings instance for the process."""

    return Settings()
