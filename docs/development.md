# Development

## Prerequisites

- Docker and Docker Compose
- [uv](https://docs.astral.sh/uv/) (Python package manager)
- Node.js 22+ and npm (for frontend work outside Docker)

## First run

```bash
cp .env.example .env
make dev
```

| URL | What |
|-----|------|
| http://localhost | App via nginx (frontend + API) — works with `make dev` and `make up` |
| http://localhost:3000 | Vite dev server with HMR (`make dev` only) |
| http://localhost/api/v1/health | BFF health (through nginx) |

`make dev` starts the dev profile with Vite HMR, all backend services, and the export stack (Redis + worker). It waits for healthchecks and runs Alembic migrations on auth and ledger databases.

Production-like stack (static frontend build inside Docker, no Vite on host port 3000):

```bash
make up
```

After changing nginx or frontend Dockerfiles, rebuild images: `make up` (includes `--build`) or `docker compose build nginx frontend && docker compose up -d`.

Stop everything:

```bash
make down
```

Run `make help` for a list of all targets.

## Makefile targets

| Target | Description |
|--------|-------------|
| `make dev` | Dev stack: `--profile dev --profile export`, then migrations |
| `make up` | Prod stack: `--profile prod --profile export`, build images, migrations |
| `make down` | Stop all profiles and remove orphans |
| `make test` | Contracts + backend unit/integration + frontend unit tests |
| `make test-e2e` | Playwright smoke against a running stack (`make dev` first) |
| `make help` | Print available targets |

### What `make test` runs

1. **Contracts** — `uv run python scripts/validate_contracts.py`
2. **BFF + export unit tests** — pytest with coverage (HTML in `coverage/bff`, `coverage/export`)
3. **Auth + ledger integration tests** — starts `integration` profile Postgres containers, runs pytest with coverage (HTML in `coverage/auth`, `coverage/ledger`)
4. **Frontend** — `npm ci`, Vitest with coverage (`frontend/coverage/`)

`make test-e2e` is separate: it requires the app stack to be running and executes Playwright smoke (`register → expense → report → export`).

## Local Python environment

One shared virtualenv at the repo root:

```bash
uv sync
```

Creates `.venv/`. Select **`.venv/bin/python`** as the interpreter in your editor.

`pyrightconfig.json` maps each `services/*` folder to the correct `app` package for import resolution.

Optional: open `spend-ledger.code-workspace` for a multi-root editor layout.

### Run a service outside Docker

PostgreSQL must be reachable (e.g. stack running via `make dev`):

```bash
cd services/bff
../../.venv/bin/python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Point `AUTH_SERVICE_URL`, `LEDGER_SERVICE_URL`, etc. at the Docker network hostnames or `localhost` ports if you publish them.

## Frontend development

Inside Docker, Vite runs with volume mounts and HMR (`frontend-dev` service).

Locally:

```bash
cd frontend
npm ci
npm run dev        # dev server on :3000; proxies /api to nginx on :80
npm run test       # Vitest unit tests
npm run test:e2e   # Playwright (stack must be up at http://localhost)
npm run lint
npm run build
```

With `make dev` running, local Vite proxies `/api` to `http://localhost` (nginx → BFF). You can also use the app entirely through http://localhost without running Vite locally.

## Environment variables

Copy `.env.example` to `.env`. Docker Compose reads it automatically.

Key groups:

| Group | Variables | Notes |
|-------|-----------|-------|
| Runtime | `APP_ENV`, `LOG_LEVEL` | `APP_ENV=production` enforces `JWT_SECRET` length ≥ 32 |
| Auth DB | `POSTGRES_AUTH_*`, `AUTH_DATABASE_URL` | Used by auth-service |
| Ledger DB | `POSTGRES_LEDGER_*`, `LEDGER_DATABASE_URL` | Used by ledger-service |
| JWT | `JWT_SECRET` | Shared by auth-service and bff (signature verification) |
| JWT (auth) | `JWT_ACCESS_EXPIRE_MINUTES`, `JWT_REFRESH_EXPIRE_DAYS` | Token lifetimes; auth-service only |
| JWT (bff) | `JWT_REFRESH_EXPIRE_DAYS` | Refresh cookie max-age on login/refresh proxy |
| Service URLs | `AUTH_SERVICE_URL`, `LEDGER_SERVICE_URL`, `EXPORT_SERVICE_URL` | Docker internal hostnames by default |
| Export | `EXPORT_ENABLED`, `REDIS_URL`, `EXPORT_FILES_DIR` | Set `EXPORT_ENABLED=false` to run without export profile |
| Debugging | `SQLALCHEMY_ECHO`, `PROFILE_REQUESTS`, `ENABLE_PYINSTRUMENT` | Ledger SQL logging and profiling (all three passed to ledger-service in compose) |
| Ports | `BFF_PORT`, `AUTH_PORT`, `LEDGER_PORT`, `EXPORT_PORT` | Internal container ports |

See `.env.example` for defaults and inline comments.

## Database migrations

Migrations run automatically on `make dev` and `make up`:

```bash
docker compose exec auth-service uv run alembic upgrade head
docker compose exec ledger-service uv run alembic upgrade head
```

Alembic configs live in `services/auth/alembic/` and `services/ledger/alembic/`.

## Contract validation

```bash
uv run python scripts/validate_contracts.py
```

For each service, the script exports FastAPI OpenAPI operations and checks them against `contracts/*.yaml`:

- All contract operations exist in the implementation
- Success response codes match
- Request bodies are declared (for internal services)
- BFF: path coverage only (public API surface)

## CI

GitHub Actions (`.github/workflows/ci.yml`) on push/PR:

| Job | What |
|-----|------|
| `contracts` | `validate_contracts.py` |
| `backend-unit` | bff + export: pytest (≥75% coverage), ruff check/format |
| `auth` | Integration pytest with Postgres service (≥75% coverage) |
| `ledger` | Alembic migrate + integration pytest (≥80% coverage) |
| `frontend` | eslint, Vitest coverage, production build |
| `e2e` | Production-like docker stack (`make up`) + nginx/app smoke + Playwright |

## TLS (optional)

Generate dev certificates:

```bash
./scripts/generate-dev-certs.sh
```

Mount results into `infra/certs/` and restart nginx. HTTP on port 80 redirects to HTTPS when certificates are present.

## Observability

- **Request ID** — BFF middleware sets `X-Request-Id` on every response
- **Structured logs** — structlog JSON logs per service
- **SQL echo** — `SQLALCHEMY_ECHO=true` on ledger (default in dev compose)
- **pyinstrument** — set `ENABLE_PYINSTRUMENT=true` on ledger for request profiling

Flower (Celery monitor) runs in the `export` + `dev` profiles at http://127.0.0.1:5555 (bound to localhost only).

## Troubleshooting

| Symptom | Check |
|---------|-------|
| `make dev` hangs on healthcheck | `docker compose ps` — wait for `/ready` on bff, auth, ledger, export-api |
| "Welcome to nginx" instead of the app | Rebuild edge nginx: `docker compose build nginx && docker compose up -d nginx` (image removes stock `default.conf`) |
| 502 from BFF | Downstream service down; check `docker compose logs bff auth-service ledger-service` |
| Export stays `pending` | `export-worker` running? Redis healthy? `docker compose logs export-worker` |
| Frontend 404 on refresh | nginx proxies `/` to frontend; use http://localhost, not a deep link without nginx |
| Integration tests fail | Ports 5433/5434 free? `make down` then retry `make test` |
| E2E fails | Stack running? `E2E_BASE_URL=http://localhost make test-e2e` |
| JWT errors in prod | `JWT_SECRET` must be ≥ 32 characters when `APP_ENV=production` |

## Pre-commit

```bash
uv run pre-commit install
```

Hooks are configured in `.pre-commit-config.yaml` (ruff, formatting, etc.).
