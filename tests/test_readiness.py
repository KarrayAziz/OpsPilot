"""Tests for concrete dependency probes and readiness invariants."""

from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest
from sqlalchemy.ext.asyncio import AsyncEngine

from opspilot.readiness import (
    PostgreSQLReadinessProbe,
    QdrantReadinessProbe,
    ReadinessService,
    ReadinessState,
)


@pytest.mark.asyncio
async def test_postgresql_probe_executes_trivial_query() -> None:
    engine = MagicMock(spec=AsyncEngine)
    connection = AsyncMock()
    connection_context = AsyncMock()
    connection_context.__aenter__.return_value = connection
    engine.connect.return_value = connection_context

    result = await PostgreSQLReadinessProbe(engine, timeout_seconds=1).check()

    assert result.status is ReadinessState.READY
    statement = connection.execute.await_args.args[0]
    assert str(statement) == "SELECT 1"


@pytest.mark.asyncio
async def test_qdrant_probe_calls_native_ready_endpoint() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/readyz"
        return httpx.Response(status_code=200)

    async with httpx.AsyncClient(
        base_url="http://qdrant.example.test:6333",
        transport=httpx.MockTransport(handler),
    ) as client:
        result = await QdrantReadinessProbe(client, timeout_seconds=1).check()

    assert result.status is ReadinessState.READY
    assert result.detail is None


@pytest.mark.asyncio
async def test_qdrant_probe_reports_non_success_status() -> None:
    transport = httpx.MockTransport(lambda _request: httpx.Response(status_code=503))

    async with httpx.AsyncClient(
        base_url="http://qdrant.example.test:6333",
        transport=transport,
    ) as client:
        result = await QdrantReadinessProbe(client, timeout_seconds=1).check()

    assert result.status is ReadinessState.UNAVAILABLE
    assert result.detail == "readiness endpoint returned HTTP 503"


def test_readiness_requires_at_least_one_real_probe() -> None:
    with pytest.raises(ValueError, match="At least one readiness probe is required"):
        ReadinessService(())
