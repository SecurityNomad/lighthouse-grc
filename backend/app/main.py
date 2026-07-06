from contextlib import asynccontextmanager
import logging

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import AsyncSessionLocal
from app.routers import risks, controls, control_mapping, evidence, tprm, audit, dashboard
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
app.include_router(evidence.router, prefix="/api/v1/evidence", tags=["evidence"], dependencies=_auth_dep)
app.include_router(tprm.router, prefix="/api/v1", tags=["tprm"], dependencies=_auth_dep)
app.include_router(audit.router, prefix="/api/v1", tags=["audit"], dependencies=_auth_dep)
app.include_router(dashboard.router, prefix="/api/v1", tags=["dashboard"], dependencies=_auth_dep)
app.include_router(plugins_router.router, prefix="/api/v1", tags=["plugins"], dependencies=_auth_dep)


@app.get("/", tags=["health"])
async def root():
    return {"status": "ok", "service": "lighthouse-api", "version": APP_VERSION}


@app.get("/health", tags=["health"])
async def health():
    return {"status": "healthy"}
