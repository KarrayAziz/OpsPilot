"""API liveness and readiness behavior tests."""

from dataclasses import dataclass

import httpx
import pytest

from opspilot.config import Settings
from opspilot.main import create_app
from opspilot.readiness import (
    DependencyReadiness,
    ReadinessService,
    ReadinessState,
)


@dataclass(slots=True)
class StubProbe:
    """Deterministic readiness probe used by API tests."""

    name: str
    result: DependencyReadiness | Exception
    calls: int = 0

    async def check(self) -> DependencyReadiness:
        self.calls += 1
        if isinstance(self.result, Exception):
            raise self.result
        return self.result


@pytest.mark.asyncio
async def test_health_is_independent_of_dependency_readiness() -> None:
    failed_probe = StubProbe("postgresql", RuntimeError("database unavailable"))
    app = create_app(
        settings=Settings(environment="test"),
        readiness_service=ReadinessService((failed_probe,)),
    )

    async with app.router.lifespan_context(app):
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert failed_probe.calls == 0


@pytest.mark.asyncio
async def test_ready_returns_200_when_all_dependencies_are_ready() -> None:
    postgres = StubProbe("postgresql", DependencyReadiness(status=ReadinessState.READY))
    qdrant = StubProbe("qdrant", DependencyReadiness(status=ReadinessState.READY))
    app = create_app(
        settings=Settings(environment="test"),
        readiness_service=ReadinessService((postgres, qdrant)),
    )

    async with app.router.lifespan_context(app):
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.get("/ready")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ready",
        "dependencies": {
            "postgresql": {"status": "ready"},
            "qdrant": {"status": "ready"},
        },
    }
    assert postgres.calls == 1
    assert qdrant.calls == 1


@pytest.mark.asyncio
async def test_ready_returns_503_and_sanitizes_probe_failures() -> None:
    postgres = StubProbe("postgresql", RuntimeError("password=must-not-leak"))
    qdrant = StubProbe("qdrant", DependencyReadiness(status=ReadinessState.READY))
    app = create_app(
        settings=Settings(environment="test"),
        readiness_service=ReadinessService((postgres, qdrant)),
    )

    async with app.router.lifespan_context(app):
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.get("/ready")

    assert response.status_code == 503
    assert response.json() == {
        "status": "unavailable",
        "dependencies": {
            "postgresql": {
                "status": "unavailable",
                "detail": "dependency check failed",
            },
            "qdrant": {"status": "ready"},
        },
    }
    assert "must-not-leak" not in response.text
    assert postgres.calls == 1
    assert qdrant.calls == 1
