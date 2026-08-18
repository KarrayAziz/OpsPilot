"""FastAPI application entry point."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import cast

import httpx
from fastapi import FastAPI, Request, Response, status
from pydantic import BaseModel

from opspilot import __version__
from opspilot.config import Settings, get_settings
from opspilot.database import create_database_engine
from opspilot.readiness import (
    PostgreSQLReadinessProbe,
    QdrantReadinessProbe,
    ReadinessResponse,
    ReadinessService,
    ReadinessState,
)


class HealthResponse(BaseModel):
    """Liveness response that does not depend on external services."""

    status: str


def create_app(
    settings: Settings | None = None,
    readiness_service: ReadinessService | None = None,
) -> FastAPI:
    """Create the API and own the lifecycle of its dependency clients."""

    resolved_settings = settings or get_settings()

    @asynccontextmanager
    async def lifespan(application: FastAPI) -> AsyncIterator[None]:
        if readiness_service is not None:
            application.state.readiness_service = readiness_service
            yield
            return

        engine = create_database_engine(resolved_settings)
        qdrant_client = httpx.AsyncClient(base_url=str(resolved_settings.qdrant_url))
        application.state.readiness_service = ReadinessService(
            (
                PostgreSQLReadinessProbe(
                    engine,
                    timeout_seconds=resolved_settings.readiness_timeout_seconds,
                ),
                QdrantReadinessProbe(
                    qdrant_client,
                    timeout_seconds=resolved_settings.readiness_timeout_seconds,
                ),
            )
        )
        try:
            yield
        finally:
            await qdrant_client.aclose()
            await engine.dispose()

    application = FastAPI(
        title=resolved_settings.app_name,
        version=__version__,
        lifespan=lifespan,
    )

    @application.get("/health", response_model=HealthResponse)
    async def health() -> HealthResponse:
        return HealthResponse(status="ok")

    @application.get(
        "/ready",
        response_model=ReadinessResponse,
        response_model_exclude_none=True,
        responses={status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ReadinessResponse}},
    )
    async def ready(request: Request, response: Response) -> ReadinessResponse:
        service = cast(ReadinessService, request.app.state.readiness_service)
        result = await service.check()
        if result.status is ReadinessState.UNAVAILABLE:
            response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return result

    return application


app = create_app()
