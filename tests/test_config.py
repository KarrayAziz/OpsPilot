"""Tests for environment-backed application configuration."""

import pytest
from pydantic import ValidationError

from opspilot.config import Settings


def test_settings_load_prefixed_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPSPILOT_APP_NAME", "Test Pilot")
    monkeypatch.setenv("OPSPILOT_ENVIRONMENT", "test")
    monkeypatch.setenv(
        "OPSPILOT_DATABASE_URL",
        "postgresql+psycopg://test-user:test-password@db.example.test:5432/test-db",
    )
    monkeypatch.setenv("OPSPILOT_QDRANT_URL", "http://qdrant.example.test:6333")
    monkeypatch.setenv("OPSPILOT_READINESS_TIMEOUT_SECONDS", "4.5")

    settings = Settings(_env_file=None)

    assert settings.app_name == "Test Pilot"
    assert settings.environment == "test"
    assert settings.database_url.get_secret_value().endswith("/test-db")
    assert str(settings.qdrant_url) == "http://qdrant.example.test:6333/"
    assert settings.readiness_timeout_seconds == 4.5


def test_settings_reject_non_positive_readiness_timeout() -> None:
    with pytest.raises(ValidationError):
        Settings(readiness_timeout_seconds=0)
