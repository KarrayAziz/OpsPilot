"""SQLAlchemy foundation shared by the application and Alembic."""

import math

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from opspilot.config import Settings


class Base(DeclarativeBase):
    """Declarative metadata root for future persisted domain models."""


def create_database_engine(settings: Settings) -> AsyncEngine:
    """Build an async PostgreSQL engine without opening a connection eagerly."""

    return create_async_engine(
        settings.database_url.get_secret_value(),
        connect_args={"connect_timeout": max(1, math.ceil(settings.readiness_timeout_seconds))},
        pool_pre_ping=True,
    )
