# Architecture

## Implemented in Phase 0

The current runtime is deliberately small:

```text
HTTP client -> FastAPI
                 |-- GET /health (process liveness)
                 `-- GET /ready
                       |-- SQLAlchemy async connection -> PostgreSQL -> SELECT 1
                       `-- HTTP client -> Qdrant -> /readyz
```

FastAPI owns the SQLAlchemy engine and Qdrant HTTP client for the application lifespan and closes
both during shutdown. Pydantic Settings validates environment input. The readiness service runs
both probes, catches and logs dependency failures, returns sanitized states, and produces HTTP
503 unless every required dependency is ready.

Alembic uses the same database URL and SQLAlchemy metadata root as the application. Phase 0 has no
domain models or schema revisions. Docker Compose runs only PostgreSQL and Qdrant; the API runs on
the host during development.

## Planned architecture (not implemented)

Later milestones are expected to add functionality bottom-up:

```text
deterministic domain services
  -> simulated enterprise adapters
  -> typed MCP capabilities
  -> knowledge retrieval and audio evidence ingestion
  -> one reasoning agent in an explicit durable LangGraph
  -> deterministic risk, approval, execution, verification, and audit services
```

The intended sensitive-action boundary is:

```text
LLM -> typed ActionProposal -> deterministic RiskEngine
    -> optional ApprovalGate -> ActionExecutor -> typed write capability -> verification
```

These components are architectural direction only. No graph, model provider, MCP server, RAG
pipeline, transcription provider, write executor, or approval mechanism exists in Phase 0.

## Dependency boundaries

Future reasoning code will consume stable business capabilities rather than database queries or
vendor APIs. Interfaces will be introduced only when a concrete adapter replacement boundary
exists; Phase 0 does not create speculative business abstractions.
