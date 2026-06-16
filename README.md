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
├── docker-compose.yml           Core stack
├── docker-compose.override.yml         Dev: hot reload, exposed ports
├── docker-compose.export.yml           Export + Redis + Celery
├── docker-compose.export.override.yml  Dev volumes for export services
└── docker-compose.test.yml             Test databases (tmpfs)
```

## Quick start

```bash
cp .env.example .env
make up
```

- App: http://localhost
- BFF (dev): http://localhost:8000/health
- Frontend (dev): http://localhost:3000

Export stack (stage 4):

```bash
make up-export
```

## Development

### Local Python environment

One shared virtualenv at the repo root (all backend dependencies):

```bash
make sync
```

Creates `.venv/` at the project root and installs per-service envs for Docker/CI lockfiles.
Select interpreter once: **`.venv/bin/python`** (already set in `.vscode/settings.json`).

`pyrightconfig.json` maps each `services/*` folder to the correct `app` package — no manual
interpreter switching when editing different services.

Optional: open **`spend-ledger.code-workspace`** in Cursor for a multi-root layout
(bff / auth / ledger / export / frontend as separate sidebar roots).

Run a service locally:

```bash
cd services/bff
../../.venv/bin/python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

PostgreSQL must be reachable (e.g. `make up`).

### Commands

```bash
make test
make lock
make migrate-ledger
```

Stage 0 checklist: `.plan/stage0-status.md` (local, gitignored with `.plan/`).

## License

Distributed under the [MIT](LICENSE) license.
