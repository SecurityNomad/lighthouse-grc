# Lighthouse GRC Platform

A minimalist GRC platform for small-to-mid SaaS companies. FastAPI backend + React frontend, running via Docker Compose.

## Stack

| Layer | Tech |
|---|---|
| Backend | Python 3.12 + FastAPI + SQLAlchemy 2.x (async) + Alembic |
| Database | PostgreSQL 16 |
| Frontend | React 18 + TypeScript + Vite + Tailwind CSS |
| Runtime | Docker Compose (3 services: db, backend, frontend) |

## Start / Stop

```bash
docker compose up          # start all services (postgres + backend + frontend)
docker compose up --build  # rebuild images first (after requirements/package changes)
docker compose down        # stop all services
```

- Frontend: http://localhost:3000
- Backend API docs: http://localhost:8000/docs
- Backend health: http://localhost:8000/health

## Backend

```bash
# Run tests (no Docker needed — uses in-memory SQLite)
cd backend && pytest -v

# Apply migrations (needs running db)
docker compose exec backend alembic upgrade head

# Generate a new migration after model changes
docker compose exec backend alembic revision --autogenerate -m "description"

# Interactive shell
docker compose exec backend python
```

**Structure:**
- `app/models/` — SQLAlchemy ORM models (UUID PKs, async-compatible)
- `app/schemas/` — Pydantic v2 schemas (RiskBase / RiskCreate / RiskUpdate / RiskRead pattern)
- `app/routers/` — FastAPI routers, one file per resource
- `app/database.py` — async engine + `get_db` dependency
- `app/config.py` — pydantic-settings; reads from `.env`
- `alembic/versions/` — migration files, named `NNNN_description.py`

**Conventions:**
- All DB operations must be async (`await db.execute(...)`)
- UUIDs as primary keys (`uuid.uuid4`)
- Enum-like string fields (impact: Critical/High/Medium/Low, status: Open/In Treatment/Closed/Accepted)
- Router prefix set in `main.py` (`/api/v1/<resource>`)

## Frontend

```bash
# Local dev without Docker (faster HMR)
cd frontend && npm install && npm run dev

# Type check
cd frontend && npm run build
```

**Structure:**
- `src/pages/` — top-level route components
- `src/components/` — reusable UI components
- `src/api/` — axios API clients, one file per resource (mirrors backend routers)
- `src/App.tsx` — router + nav layout
- API base URL proxied via Vite (`/api` → `http://localhost:8000`)

**Conventions:**
- `useQuery` from TanStack Query for all data fetching
- `risksApi.list()`, `risksApi.create()` etc. — typed functions in `src/api/risks.ts`
- Tailwind utility classes only, no custom CSS files
- Colour-coded badges for impact (red/orange/yellow/green) and status (blue/purple/gray/green)

## Project Scope

Core modules (phased delivery):
1. **Risk Register** ← Phase 1 (current)
2. Control Framework Library (YAML-defined: SOC 2, ISO 27001, CIS Controls)
3. Control Mapping (many-to-many across frameworks)
4. Evidence Collection (manual upload + automated plugins)
5. TPRM Module (vendor register + tiering + questionnaires)
6. Audit Management (plans, findings, closure tracking)
7. Dashboard (heatmap, coverage %, evidence freshness)

Plugins (Phase 3): AWS Config/Security Hub, MISP (threat intel), Slack (notifications).

**New features go to `FUTURE.md` unless they are in the above list.**

## Key Files

- `docs/adr/ADR-001-platform-philosophy-and-scope.md` — read this before proposing architectural changes
- `.env.example` — copy to `.env` before first run
- `PM/` — project management artefacts (charter, WBS, schedule); not part of the application
