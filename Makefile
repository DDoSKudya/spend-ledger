COMPOSE := docker compose
COMPOSE_INTEGRATION := COMPOSE_PROJECT_NAME=spend-ledger-integration $(COMPOSE) --profile integration

SERVICES := bff auth ledger export
AUTH_DATABASE_URL ?= postgresql+asyncpg://spend_auth:change_me_auth@localhost:5432/auth_db
LEDGER_DATABASE_URL ?= postgresql+asyncpg://spend_ledger:change_me_ledger@localhost:5432/ledger_db

.PHONY: dev up down logs sync test test-backend test-frontend lock migrate-auth migrate-ledger test-ledger-integration verify pre-commit-install pre-commit _migrate

dev:
	$(COMPOSE) up -d --wait
	@$(MAKE) --no-print-directory _migrate

up:
	$(COMPOSE) --profile export up -d --wait
	@$(MAKE) --no-print-directory _migrate

down:
	$(COMPOSE) --profile export down

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
	cd services/bff && uv run pytest && \
	cd ../auth && uv run pytest && \
	cd ../ledger && uv run pytest && \
	cd ../export && uv run pytest

test-frontend:
	cd frontend && npm run lint && npm run build

lock:
	uv lock
	cd services/bff && uv lock
	cd services/auth && uv lock
	cd services/ledger && uv lock
	cd services/export && uv lock

migrate-auth:
	cd services/auth && AUTH_DATABASE_URL=$(AUTH_DATABASE_URL) ../../.venv/bin/python -m alembic upgrade head

migrate-ledger:
	cd services/ledger && LEDGER_DATABASE_URL=$(LEDGER_DATABASE_URL) ../../.venv/bin/python -m alembic upgrade head

_migrate:
	$(COMPOSE) exec -T auth-service uv run alembic upgrade head
	$(COMPOSE) exec -T ledger-service uv run alembic upgrade head

test-ledger-integration:
	$(COMPOSE_INTEGRATION) up -d --wait postgres-integration
	cd services/ledger && \
	LEDGER_INTEGRATION=1 \
	LEDGER_DATABASE_URL=postgresql+asyncpg://spend_ledger_test:test_ledger@localhost:5433/ledger_db_test \
	APP_ENV=test \
	../../.venv/bin/python -m pytest tests/test_crud.py tests/test_schemas.py tests/test_filters.py -q
	$(COMPOSE_INTEGRATION) down

verify: test
	@echo "==> API smoke (nginx → BFF auth → ledger)"
	@curl -sf http://localhost/api/v1/health >/dev/null
	@EMAIL=verify-$$(date +%s)@example.com; \
	PASS=supersecret; \
	curl -sf -X POST http://localhost/api/v1/auth/register \
		-H 'Content-Type: application/json' \
		-d "{\"email\":\"$$EMAIL\",\"password\":\"$$PASS\"}" >/dev/null; \
	TOKEN=$$(curl -sf -X POST http://localhost/api/v1/auth/login \
		-H 'Content-Type: application/json' \
		-d "{\"email\":\"$$EMAIL\",\"password\":\"$$PASS\"}" | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])"); \
	NAME=verify-$$(date +%s); \
	curl -sf -X POST http://localhost/api/v1/categories \
		-H "Authorization: Bearer $$TOKEN" \
		-H 'Content-Type: application/json' \
		-d "{\"name\":\"$$NAME\"}" | grep -q "$$NAME"
	@echo "verify OK"

pre-commit-install:
	uv run pre-commit install

pre-commit:
	uv run pre-commit run --all-files
