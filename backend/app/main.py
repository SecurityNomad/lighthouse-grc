from contextlib import asynccontextmanager
from pathlib import Path
import logging

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import AsyncSessionLocal
from app.routers import risks, controls, control_mapping, evidence, tprm, audit, dashboard, soa
from app.routers import auth as auth_router, clients as clients_router, admin as admin_router
from app.routers import plugins as plugins_router
from app.seed import seed_frameworks, seed_vendor_questions, seed_admin_user
from app.auth import get_current_user, enforce_write_permission
from app.seed_demo import seed_demo_data
import app.plugins  # noqa: F401 — registers the built-in plugins with the registry

APP_VERSION = "1.3.0"

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with AsyncSessionLocal() as session:
        try:
            await seed_frameworks(session)
        except Exception:
            logger.exception("Framework seeding failed — continuing startup")
    async with AsyncSessionLocal() as session:
        try:
            await seed_vendor_questions(session)
        except Exception:
            logger.exception("Vendor question seeding failed — continuing startup")
    async with AsyncSessionLocal() as session:
        try:
            await seed_admin_user(session)
        except Exception:
            logger.exception("Admin user seeding failed — continuing startup")
    if settings.seed_demo_data:
        async with AsyncSessionLocal() as session:
            try:
                await seed_demo_data(session)
            except Exception:
                logger.exception("Demo data seeding failed — continuing startup")
    yield


app = FastAPI(
    title="Lighthouse GRC Platform",
    description="A minimalist, opinionated GRC platform for small-to-mid SaaS companies.",
    version=APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Resource routers authenticate every request and reject writes from read-only
# (viewer) roles via enforce_write_permission. auth/admin/clients manage their
# own authorization (login is public; admin routes require the admin role).
_auth_dep = [Depends(enforce_write_permission)]

app.include_router(auth_router.router, prefix="/api/v1", tags=["auth"])
app.include_router(admin_router.router, prefix="/api/v1", tags=["admin"])
app.include_router(clients_router.router, prefix="/api/v1", tags=["clients"], dependencies=[Depends(get_current_user)])
app.include_router(risks.router, prefix="/api/v1/risks", tags=["risks"], dependencies=_auth_dep)
app.include_router(controls.router, prefix="/api/v1", tags=["controls"], dependencies=_auth_dep)
app.include_router(control_mapping.router, prefix="/api/v1", tags=["control-mapping"], dependencies=_auth_dep)
app.include_router(soa.router, prefix="/api/v1", tags=["soa"], dependencies=_auth_dep)
app.include_router(evidence.router, prefix="/api/v1/evidence", tags=["evidence"], dependencies=_auth_dep)
app.include_router(tprm.router, prefix="/api/v1", tags=["tprm"], dependencies=_auth_dep)
app.include_router(audit.router, prefix="/api/v1", tags=["audit"], dependencies=_auth_dep)
app.include_router(dashboard.router, prefix="/api/v1", tags=["dashboard"], dependencies=_auth_dep)
app.include_router(plugins_router.router, prefix="/api/v1", tags=["plugins"], dependencies=_auth_dep)


@app.get("/health", tags=["health"])
async def health():
    return {"status": "healthy"}


# ---------------------------------------------------------------------------
# Static frontend (single-app deployment)
#
# In the Docker Compose development setup the frontend is served separately by
# Vite, and this block is inert. In the Fly.io image the multi-stage build drops
# the compiled SPA at settings.static_dir, and the API process serves it too —
# one machine instead of two, and no CORS between them.
#
# Mounted last so every /api/v1, /docs, /redoc, and /health route above wins.
# ---------------------------------------------------------------------------
_static_dir = Path(settings.static_dir)

if _static_dir.is_dir():
    app.mount(
        "/assets",
        StaticFiles(directory=_static_dir / "assets"),
        name="assets",
    )

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str):
        """Serve the built SPA, falling back to index.html for client routes.

        A request for an unknown /api/... path must still 404 as JSON rather
        than silently returning the HTML shell, which would turn an API typo
        into a confusing parse error on the client.
        """
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="Not found")

        candidate = (_static_dir / full_path).resolve()
        # Containment check — never serve outside the static root.
        if (
            full_path
            and _static_dir.resolve() in candidate.parents
            and candidate.is_file()
        ):
            return FileResponse(candidate)

        return FileResponse(_static_dir / "index.html")

else:
    @app.get("/", tags=["health"])
    async def root():
        return {"status": "ok", "service": "lighthouse-api", "version": APP_VERSION}
