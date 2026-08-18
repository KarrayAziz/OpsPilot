.PHONY: install run test lint typecheck docker-up docker-down migrate migration

install:
	uv sync --all-groups

run:
	uv run uvicorn opspilot.main:app --reload

test:
	uv run pytest

lint:
	uv run ruff check .

typecheck:
	uv run mypy .

docker-up:
	docker compose up -d

docker-down:
	docker compose down

migrate:
	uv run alembic upgrade head

migration:
	@test -n "$(message)" || (echo "usage: make migration message='describe change'" && exit 1)
	uv run alembic revision --autogenerate -m "$(message)"
