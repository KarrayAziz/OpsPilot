# OpsPilot

OpsPilot is a production-oriented portfolio project for reliable agentic automation in a
synthetic B2B SaaS environment. The long-term product will investigate operational requests,
ground decisions in enterprise evidence, gate sensitive actions deterministically, and preserve
an auditable workflow history.

## Current status: Phase 0

Only the project foundation is implemented:

- a Python 3.12 project managed by `uv`;
- a minimal FastAPI service with liveness and dependency readiness endpoints;
- validated environment configuration with Pydantic Settings;
- an async SQLAlchemy engine and Alembic migration environment;
- local PostgreSQL and Qdrant services through Docker Compose;
- pytest, Ruff, and mypy configuration and tests.

Business workflows, domain tables, LangGraph, model calls, MCP, RAG ingestion, transcription,
approval handling, and a frontend are **planned and not implemented**.

## Prerequisites

- Python 3.12
- [`uv`](https://docs.astral.sh/uv/)
- Docker with Docker Compose

## Local setup

```bash
cp .env.example .env
make install
make docker-up
make migrate
make run
```

The committed values in `.env.example` are local-only examples, not secrets. Use independent,
secret-managed credentials outside local development. `.env` is ignored by Git.

Verify the service:

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/ready
```

`GET /health` is a process liveness check and does not contact dependencies. `GET /ready`
executes `SELECT 1` through SQLAlchemy against PostgreSQL and calls Qdrant's `/readyz` endpoint.
It returns HTTP 200 only when both checks pass; otherwise it returns HTTP 503 with sanitized
per-dependency states.

## Commands

| Command | Purpose |
| --- | --- |
| `make install` | Create/update the `uv` environment and install all dependency groups |
| `make run` | Run the FastAPI development server |
| `make test` | Run deterministic tests |
| `make lint` | Run Ruff checks |
| `make typecheck` | Run mypy in strict mode |
| `make docker-up` | Start PostgreSQL and Qdrant |
| `make docker-down` | Stop the local services without deleting their named volumes |
| `make migrate` | Apply all Alembic migrations |
| `make migration message='description'` | Generate a future schema migration |

The equivalent direct commands are visible in the [Makefile](Makefile). Phase 0 intentionally
has no schema revision because it introduces no domain tables.

## Configuration

Application variables use the `OPSPILOT_` prefix. The full local template is
[`.env.example`](.env.example).

| Variable | Purpose |
| --- | --- |
| `OPSPILOT_DATABASE_URL` | SQLAlchemy PostgreSQL connection URL |
| `OPSPILOT_QDRANT_URL` | Qdrant HTTP base URL |
| `OPSPILOT_READINESS_TIMEOUT_SECONDS` | Per-dependency timeout, greater than 0 and at most 30 seconds |
| `OPSPILOT_ENVIRONMENT` | `development`, `test`, or `production` |
| `OPSPILOT_LOG_LEVEL` | Validated application log level |

## Documentation

- [Product scope](docs/PRODUCT.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Domain model](docs/DOMAIN_MODEL.md)
- [Security](docs/SECURITY.md)
- [Evaluation](docs/EVALUATION.md)
- [Audio](docs/AUDIO.md)

The repository-wide engineering constraints are defined in [AGENTS.md](AGENTS.md).
