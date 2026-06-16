COMPOSE := docker compose
COMPOSE_EXPORT := $(COMPOSE) -f docker-compose.yml -f docker-compose.export.yml
COMPOSE_EXPORT_DEV := $(COMPOSE_EXPORT) -f docker-compose.override.yml -f docker-compose.export.override.yml

SERVICES := bff auth ledger export

.PHONY: up up-export down logs sync test test-backend test-frontend lock migrate-ledger

up:
	$(COMPOSE) -f docker-compose.yml -f docker-compose.override.yml up -d

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
	cd services/ledger && ../../.venv/bin/python -m alembic upgrade head
