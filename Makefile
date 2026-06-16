COMPOSE := docker compose
COMPOSE_DEV := $(COMPOSE) -f docker-compose.yml -f docker-compose.override.yml
COMPOSE_INTEGRATION := $(COMPOSE) -f docker-compose.integration.yml
COMPOSE_EXPORT := $(COMPOSE) -f docker-compose.yml -f docker-compose.export.yml
COMPOSE_EXPORT_DEV := $(COMPOSE_EXPORT) -f docker-compose.override.yml -f docker-compose.export.override.yml

SERVICES := bff auth ledger export
LEDGER_DATABASE_URL ?= postgresql+asyncpg://spend_ledger:change_me_ledger@localhost:5432/ledger_db

.PHONY: up up-export down logs sync test test-backend test-frontend lock migrate-ledger migrate-ledger-docker test-ledger-integration verify pre-commit-install pre-commit

up:
	$(COMPOSE_DEV) up -d --wait
	$(MAKE) migrate-ledger-docker

up-export:
	$(COMPOSE_EXPORT_DEV) up -d

down:
	-$(COMPOSE_EXPORT) down
	$(COMPOSE) down

logs:
	$(COMPOSE) logs -f

sync:
	uv sync --dev
	@for svc in $(SERVICES); do \
		echo "==> services/$$svc (docker/CI lockfile)"; \
		(cd services/$$svc && uv sync --dev) || exit 1; \
	done
	@echo "==> frontend"
	cd frontend && npm ci

test: test-backend test-frontend

test-backend:
	cd services/bff && ../../.venv/bin/python -m pytest && \
	cd ../auth && ../../.venv/bin/python -m pytest && \
	cd ../ledger && ../../.venv/bin/python -m pytest && \
	cd ../export && ../../.venv/bin/python -m pytest

test-frontend:
	cd frontend && npm run lint && npm run build

lock:
	uv lock
	cd services/bff && uv lock
	cd services/auth && uv lock
	cd services/ledger && uv lock
	cd services/export && uv lock

migrate-ledger:
	cd services/ledger && LEDGER_DATABASE_URL=$(LEDGER_DATABASE_URL) ../../.venv/bin/python -m alembic upgrade head

migrate-ledger-docker:
	$(COMPOSE_DEV) exec -T ledger-service uv run alembic upgrade head

test-ledger-integration:
	$(COMPOSE_INTEGRATION) up -d --wait
	cd services/ledger && \
	LEDGER_INTEGRATION=1 \
	LEDGER_DATABASE_URL=postgresql+asyncpg://spend_ledger_test:test_ledger@localhost:5433/ledger_db_test \
	APP_ENV=test \
	../../.venv/bin/python -m pytest tests/test_crud.py tests/test_schemas.py -q
	$(COMPOSE_INTEGRATION) down

verify: test
	@echo "==> API smoke (nginx → BFF → ledger)"
	@curl -sf http://localhost/api/v1/health >/dev/null
	@NAME=verify-$$(date +%s); \
	curl -sf -X POST http://localhost/api/v1/categories \
		-H 'Content-Type: application/json' \
		-d "{\"name\":\"$$NAME\"}" | grep -q "$$NAME"
	@curl -sf http://localhost/api/v1/categories | grep -q '\['
	@echo "verify OK"

pre-commit-install:
	uv run pre-commit install

pre-commit:
	uv run pre-commit run --all-files
