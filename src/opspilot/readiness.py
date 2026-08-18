"""Dependency readiness probes used by the HTTP readiness endpoint."""

import asyncio
import logging
from collections.abc import Sequence
from enum import StrEnum
from typing import Protocol

import httpx
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

logger = logging.getLogger(__name__)


class ReadinessState(StrEnum):
    """Possible states for the application and each required dependency."""

    READY = "ready"
    UNAVAILABLE = "unavailable"


class DependencyReadiness(BaseModel):
    """Sanitized readiness result for one dependency."""

    status: ReadinessState
    detail: str | None = None


class ReadinessResponse(BaseModel):
    """Aggregate readiness response returned by the API."""

    status: ReadinessState
    dependencies: dict[str, DependencyReadiness]


class ReadinessProbe(Protocol):
    """A concrete check for one required runtime dependency."""

    name: str

    async def check(self) -> DependencyReadiness:
        """Check the dependency and return its sanitized state."""


class PostgreSQLReadinessProbe:
    """Verify that PostgreSQL accepts a connection and a trivial query."""

    name = "postgresql"

    def __init__(self, engine: AsyncEngine, timeout_seconds: float) -> None:
        self._engine = engine
        self._timeout_seconds = timeout_seconds

    async def check(self) -> DependencyReadiness:
        async with asyncio.timeout(self._timeout_seconds):
            async with self._engine.connect() as connection:
                await connection.execute(text("SELECT 1"))
        return DependencyReadiness(status=ReadinessState.READY)


class QdrantReadinessProbe:
    """Verify Qdrant through its native readiness endpoint."""

    name = "qdrant"

    def __init__(self, client: httpx.AsyncClient, timeout_seconds: float) -> None:
        self._client = client
        self._timeout_seconds = timeout_seconds

    async def check(self) -> DependencyReadiness:
        response = await self._client.get("/readyz", timeout=self._timeout_seconds)
        if response.status_code != httpx.codes.OK:
            return DependencyReadiness(
                status=ReadinessState.UNAVAILABLE,
                detail=f"readiness endpoint returned HTTP {response.status_code}",
            )
        return DependencyReadiness(status=ReadinessState.READY)


class ReadinessService:
    """Run all required probes and compute application readiness."""

    def __init__(self, probes: Sequence[ReadinessProbe]) -> None:
        if not probes:
            msg = "At least one readiness probe is required"
            raise ValueError(msg)

        names = [probe.name for probe in probes]
        if len(names) != len(set(names)):
            msg = "Readiness probe names must be unique"
            raise ValueError(msg)

        self._probes = tuple(probes)

    async def check(self) -> ReadinessResponse:
        results = await asyncio.gather(*(self._run_probe(probe) for probe in self._probes))
        dependencies = {
            probe.name: result for probe, result in zip(self._probes, results, strict=True)
        }
        overall = (
            ReadinessState.READY
            if all(result.status is ReadinessState.READY for result in results)
            else ReadinessState.UNAVAILABLE
        )
        return ReadinessResponse(status=overall, dependencies=dependencies)

    @staticmethod
    async def _run_probe(probe: ReadinessProbe) -> DependencyReadiness:
        try:
            return await probe.check()
        except Exception:
            logger.warning("Readiness probe failed: %s", probe.name, exc_info=True)
            return DependencyReadiness(
                status=ReadinessState.UNAVAILABLE,
                detail="dependency check failed",
            )
