# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-07-02

Frontend UI refresh, TypeScript migration, and platform improvements.

### Added

- Project documentation hub: `docs/architecture.md`, `docs/development.md`
- `make help` with self-describing Makefile targets
- OpenAPI contract descriptions for auth cookie flow and export polling
- Export worker healthcheck (Celery inspect ping)
- Flower UI on host port 5555 in dev/export profiles
- Atelier UI layout: top navigation, mobile tab bar, split views, drawer-based expense form
- Shared design tokens (`tokens.css`, `layout.css`, `components.css`, `motion.css`, `transitions.css`)
- Mint accent palette, Inter typography, and light-only theme
- App icon and favicon (`public/icons/app-icon.svg`, `public/favicon.svg`)
- Structured motion: page fade, auth↔app shell transition, loading/content swaps
- Table scroll regions with sticky headers, keyboard focus styling, and list scroll containers
- TypeScript across frontend: typed props/emits, domain models, `vue-tsc` typecheck script
- Lazy-loaded routes and Pinia auth store in Composition API (setup store) style
- `ConfirmDialog`, `ToastHost`, `AuthLayout`, `NamedResourcePanel`, `ExpenseListItem` components

### Changed

- README rewritten as navigation hub (links to docs, contracts, changelog)
- `.env.example` grouped with inline comments
- `getErrorMessage` maps known API `code` values and native `Error.message`
- `apiBlob` parses JSON error bodies from failed downloads
- `make test` enforces the same coverage thresholds as CI
- nginx TLS: `conf.d` include, HTTP→HTTPS redirect when certs are present
- BFF `/ready` and proxy handle httpx connection errors
- nginx Docker image removes stock `default.conf` so the app proxy is not shadowed
- CI e2e uses production-like stack (`make up`) and checks nginx serves the SPA
- Export worker streams ledger pages to disk without loading all rows into memory
- Vite dev proxy targets nginx on port 80
- Flower bound to `127.0.0.1:5555` only
- Migrated frontend source from JavaScript to TypeScript (`.ts`, `<script setup lang="ts">`)
- Rebuilt all views and shared UI components on the new design system
- ESLint configured for Vue + TypeScript (`typescript-eslint`, `vue-eslint-parser`)

### Fixed

- nginx `default.conf` from base image shadowed app routing (`Welcome to nginx` on `make up`)
- Export polling timeout message visible in UI
- `ENABLE_PYINSTRUMENT` and `PROFILE_REQUESTS` defaults aligned between compose and `.env.example`
- Export service `RequestIdMiddleware` includes `service` in structlog context
- Removed unused `JWT_ACCESS_EXPIRE_MINUTES` from BFF config
- Vite dev server blank page after TS migration (`resolve.extensionAlias` maps `.js` imports to `.ts`)
- Export composable registers `onUnmounted` only inside an active component instance

## [1.0.0] - 2026-06-17

First production-ready MVP release of Spend Ledger.

### Added

#### Platform and infrastructure

- Monorepo with four backend services (`bff`, `auth`, `ledger`, `export`) and Vue 3 frontend
- Single `docker-compose.yml` with profiles: `dev`, `prod`, `export`, `integration`
- Makefile targets: `dev`, `up`, `test`, `down`
- nginx reverse proxy: `/` → frontend, `/api/` → BFF
- Optional TLS via `infra/certs` and `scripts/generate-dev-certs.sh`
- Kubernetes-friendly `/ready` probes on auth, ledger, export, and BFF
- Production port hardening: internal services are not published on the host (access via nginx `:80`/`:443`)
- Alembic migrations for `auth_db` and `ledger_db`
- Versioned OpenAPI contracts in `contracts/`
- Contract validation script: `scripts/validate_contracts.py` (operations, response codes, request bodies)
- CI: backend unit/integration tests, frontend unit tests, contract validation, Playwright E2E smoke

#### Auth service

- User registration and login with argon2 password hashing
- JWT access tokens and refresh token rotation
- Logout with refresh token revocation
- Bearer token verification endpoint
- Per-user data isolation via BFF `X-User-Id` header

#### Ledger service

- CRUD for categories, tags, and expenses
- Many-to-many expense ↔ tags relationship
- Category delete protection when expenses exist (409)
- Duplicate name handling for categories and tags (409)
- Expense list filters: category, tags (OR semantics), date range, search
- Pagination and sorting (`expense_date`, `amount`, `created_at`)
- Monthly aggregated reports with optional category filter
- SQL profiling middleware and optional pyinstrument profiling (`ENABLE_PYINSTRUMENT=true`)
- Integration tests with equivalence-class coverage

#### Export service

- Async CSV and XLSX export via Celery worker and Redis
- Job status polling: `pending` → `processing` → `done` / `failed`
- Idempotent export retries
- Paginated reads from ledger service
- Load test for 1200-row CSV export

#### BFF

- Public API under `/api/v1/*`
- httpOnly refresh cookie flow
- JWT auth middleware for protected routes
- Transparent proxy to auth, ledger, and export services
- Export download URL injection when job completes

#### Frontend

- Pages: login, register, expenses, categories, tags, reports, export
- Composables: `useAuth`, `useExpenses`, `useCategories`, `useTags`, `useExport`
- API client with automatic 401 refresh retry
- Tailwind CSS UI with Heroicons
- Vitest unit tests with coverage thresholds
- Playwright E2E smoke: register → expense → report → export (CSV download)
- 404 page and empty states for categories, tags, expenses, and reports

### Changed

- Unified API error responses: `{ "detail": "...", "code": "..." }` across all services
- BFF auth routes use `AppError` instead of ad-hoc `JSONResponse` for client errors
- Contract validation checks success response codes and request bodies (auth, ledger, export)
- `make dev` + export profile; nginx resolves `frontend-dev` via network alias `frontend`
- Project version set to `1.0.0` across services
- `JWT_SECRET` validation in production (minimum 32 characters)

### Security

- Refresh tokens stored server-side with rotation
- Internal services not exposed on host ports in production compose layout
- Documented strong `JWT_SECRET` requirement in `.env.example`

## [0.1.0] - 2026-06-16

Initial repository scaffold.

### Added

- Project layout, MIT license, `.env.example`, `.gitignore`
- Basic README and changelog structure
