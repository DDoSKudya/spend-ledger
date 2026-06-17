# Spend Ledger

Personal expense tracking: categories, tags, filters, monthly reports, and CSV/XLSX export.

## Quick start

```bash
cp .env.example .env
make dev
```

Open http://localhost — nginx serves the frontend and proxies `/api/` to the BFF.

| URL | Purpose |
|-----|---------|
| http://localhost | App via nginx (use for both `make dev` and `make up`) |
| http://localhost:3000 | Vite dev server with HMR (`make dev` only) |
| http://localhost/api/v1/health | BFF health |

| Command | Stack |
|---------|-------|
| `make dev` | Vite HMR + backend + export (daily development) |
| `make up` | Built frontend (no Vite) + backend + export (production-like) |

Stop: `make down` · All commands: `make help`

## Stack

Python 3.12 · FastAPI · PostgreSQL · Redis/Celery · Vue 3 · Vite · Tailwind · Docker Compose · nginx

## Documentation

| Topic | Location |
|-------|----------|
| Architecture, auth/export flows, error codes | [docs/architecture.md](docs/architecture.md) |
| Development, testing, CI, troubleshooting | [docs/development.md](docs/development.md) |
| API contracts (OpenAPI) | [contracts/](contracts/) |
| Changelog | [CHANGELOG.md](CHANGELOG.md) |
| Environment variables | [.env.example](.env.example) |

## Repository layout

```
spend-ledger/
├── contracts/       OpenAPI specs (bff, auth, ledger, export)
├── docs/            Guides
├── frontend/        Vue SPA
├── infra/           Docker, nginx, TLS
├── services/
│   ├── bff/         Public API gateway
│   ├── auth/        Authentication
│   ├── ledger/      Expenses, categories, tags, reports
│   └── export/      Background export jobs
├── docker-compose.yml
├── Makefile
└── pyproject.toml   Shared Python dev environment (uv)
```

## License

Distributed under the [MIT](LICENSE) license.
