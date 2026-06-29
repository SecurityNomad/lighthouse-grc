---
name: project-v1-status
description: Lighthouse GRC v1.1 status — auth, multi-client, dark mode added after v1.0 ship
metadata:
  type: project
---

All 7 modules complete (Risk, Controls, Control Mapping, Evidence, TPRM, Audit, Dashboard). 52 tests pass.

**v1.0** shipped 2026-06-16. **v1.1** shipped 2026-06-29 with three major additions:

1. **JWT Authentication**: `POST /auth/token`, `GET /auth/me`; User model; bcrypt passwords; default admin seeded on startup (`admin@lighthouse.local` / `changeme`). Router-level `Depends(get_current_user)` on all data routers.

2. **Multi-client consulting model**: Client CRUD (`/clients`). Optional `client_id` FK on risks, evidence, vendors, audit_plans. List endpoints filter by `?client_id=`. Create endpoints accept `?client_id=` query param. Frontend axios interceptor injects both Bearer token and client_id automatically.

3. **Dark mode + collapsible sidebar**: Tailwind `darkMode: 'class'`. Sidebar always `bg-slate-900`; collapses to 64px icons-only. Dark mode toggle persists to localStorage. Client selector in sidebar. LoginPage at `/login`.

**New files (v1.1)**:
- Backend: `app/auth.py`, `app/models/user.py`, `app/models/client.py`, `app/schemas/user.py`, `app/schemas/client.py`, `app/routers/auth.py`, `app/routers/clients.py`, `alembic/versions/0008-0010`
- Frontend: `src/api/client.ts` (shared axios), `src/api/auth.ts`, `src/api/clients.ts`, `src/contexts/AuthContext.tsx`, `src/contexts/ClientContext.tsx`, `src/components/Sidebar.tsx`, `src/pages/LoginPage.tsx`, `src/pages/ClientsPage.tsx`

**Why**: User wants to use the platform as a GRC analyst/engineer assessing multiple clients (hospitals, insurers, airlines). Each client gets their own scoped data.

**How to apply**: When extending the platform, new data models should also get `client_id` FK and list endpoint filtering. Auth is already enforced globally via `main.py` router includes.
