COMPOSE := docker compose
COMPOSE_INTEGRATION := $(COMPOSE) --profile integration

LEDGER_DATABASE_URL := postgresql+asyncpg://spend_ledger_test:test_ledger@localhost:5433/ledger_db_test
AUTH_DATABASE_URL := postgresql+asyncpg://spend_auth_test:test_auth@localhost:5434/auth_db_test

.DEFAULT_GOAL := help

.PHONY: help dev up test down test-e2e _migrate _test-contracts _test-bff-export _test-integration _test-frontend _test-e2e

help: ## Show available targets
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-14s %s\n", $$1, $$2}'

# test: unit + integration (no Docker app stack). test-e2e: Playwright against running stack (make dev first).

dev: ## Dev stack (Vite + services + export) and run migrations
	$(COMPOSE) --profile dev --profile export up -d --wait
	@$(MAKE) --no-print-directory _migrate

up: ## Production stack (built frontend + export) and run migrations
	$(COMPOSE) --profile prod --profile export up -d --wait --build
	@$(MAKE) --no-print-directory _migrate

down: ## Stop all compose profiles
	-$(COMPOSE) --profile dev --profile prod --profile export --profile integration down --remove-orphans

test: ## Run contracts, backend, and frontend tests
	@$(MAKE) --no-print-directory _test-contracts _test-bff-export _test-integration _test-frontend

test-e2e: ## Playwright smoke (requires make dev)
	@$(MAKE) --no-print-directory _test-e2e

_test-contracts:
	@echo "==> contracts"
	@uv run python scripts/validate_contracts.py

_test-bff-export:
	@for svc in bff export; do \
		echo "==> services/$$svc"; \
		(cd services/$$svc && uv run pytest \
			--cov=app \
			--cov-report=term-missing:skip-covered \
			--cov-report=html:../../coverage/$$svc \
			--cov-fail-under=75) || exit 1; \
	done

_test-integration:
	$(COMPOSE_INTEGRATION) up -d --wait postgres-integration postgres-auth-integration
	@status=0; \
	echo "==> services/auth"; \
	(cd services/auth && \
		export AUTH_INTEGRATION=1 && \
		export AUTH_DATABASE_URL=$(AUTH_DATABASE_URL) && \
		export APP_ENV=test && \
		uv run pytest \
			--cov=app \
			--cov-report=term-missing:skip-covered \
			--cov-report=html:../../coverage/auth \
			--cov-fail-under=75) || status=1; \
	echo "==> services/ledger"; \
	(cd services/ledger && \
		export LEDGER_INTEGRATION=1 && \
		export LEDGER_DATABASE_URL=$(LEDGER_DATABASE_URL) && \
		export APP_ENV=test && \
		uv run alembic upgrade head && \
		uv run pytest \
			--cov=app \
			--cov-report=term-missing:skip-covered \
			--cov-report=html:../../coverage/ledger \
			--cov-fail-under=80) || status=1; \
	$(COMPOSE_INTEGRATION) stop postgres-integration postgres-auth-integration; \
	exit $$status

_test-frontend:
	@echo "==> frontend"
	@cd frontend && npm ci --silent && npm run test:coverage

_test-e2e:
	@echo "==> e2e (requires app stack: make dev)"
	@cd frontend && npm ci --silent && npx playwright install chromium
	@cd frontend && npm run test:e2e

_migrate:
	$(COMPOSE) exec -T auth-service uv run alembic upgrade head
	$(COMPOSE) exec -T ledger-service uv run alembic upgrade head
