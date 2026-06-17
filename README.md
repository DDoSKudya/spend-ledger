# Spend Ledger

A personal expense tracking and financial ledger application.

## Stack

- Backend: Python 3.12, FastAPI, uv, PostgreSQL, Redis, Celery
- Frontend: Vue 3, Vite, JavaScript, Tailwind CSS
- Infra: Docker Compose, nginx

## Repository layout

```
spend-ledger/
├── contracts/           OpenAPI contracts (versioned)
├── frontend/            Vue SPA
├── pyproject.toml       Root dev environment (shared .venv)
├── pyrightconfig.json   IDE: per-service import resolution
├── spend-ledger.code-workspace  Optional multi-root Cursor layout
├── infra/
│   ├── docker/python-service.Dockerfile  Shared Python service image (Alpine)
│   └── nginx/         Reverse proxy config
├── services/
│   ├── bff/             Public API gateway
│   ├── auth/            Authentication
│   ├── ledger/          Expenses, categories, tags, reports
│   └── export/          Background export jobs
└── docker-compose.yml           Dev stack (+ profiles: export, integration)
```

## Quick start

```bash
cp .env.example .env
make dev
```

- App: http://localhost
- BFF (dev): http://localhost:8000/health
- Frontend (dev): http://localhost:3000

Full stack (export, Redis, Celery):

```bash
make up
```

## Development

### Local Python environment

One shared virtualenv at the repo root (all backend dependencies):

```bash
make sync
```

Creates `.venv/` at the project root and installs per-service envs for Docker/CI lockfiles.
Select interpreter: **`.venv/bin/python`** (Cursor/VS Code: Python: Select Interpreter).

Install git hooks (ruff lint + format on commit):

```bash
make pre-commit-install
```

`pyrightconfig.json` maps each `services/*` folder to the correct `app` package — no manual
interpreter switching when editing different services.

Optional: open **`spend-ledger.code-workspace`** locally for a multi-root layout
(bff / auth / ledger / export / frontend as separate sidebar roots).

Run a service locally:

```bash
cd services/bff
../../.venv/bin/python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

PostgreSQL must be reachable (e.g. `make dev`).

### Commands

```bash
make dev                 # core stack (nginx, frontend, bff, auth, ledger)
make up                  # full stack (+ export, redis, celery)
make down                # stop all containers
make logs
make test
make verify              # test + API smoke (nginx → BFF → ledger)
make test-ledger-integration   # ledger CRUD tests (isolated Postgres :5433)
make pre-commit
make lock
make migrate-ledger        # from host (needs Postgres on :5432)
```

`make dev` and `make up` wait for healthchecks and run Alembic migrations automatically.

Stage checklists: `.plan/stage0-status.md` … `stage4-status.md` (local, gitignored with `.plan/`).  
**Текущий фокус:** этап 5 — Frontend UI.

## License

Distributed under the [MIT](LICENSE) license.
