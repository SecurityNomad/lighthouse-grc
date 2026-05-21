from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import AsyncSessionLocal
from app.routers import risks, controls
from app.seed import seed_frameworks

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with AsyncSessionLocal() as session:
        try:
            await seed_frameworks(session)
        except Exception:
            logger.exception("Framework seeding failed — continuing startup")
    yield


app = FastAPI(
    title="Lighthouse GRC Platform",
    description="A minimalist, opinionated GRC platform for small-to-mid SaaS companies.",
    version="0.1.0",
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

app.include_router(risks.router, prefix="/api/v1/risks", tags=["risks"])
app.include_router(controls.router, prefix="/api/v1", tags=["controls"])


@app.get("/", tags=["health"])
async def root():
    return {"status": "ok", "service": "lighthouse-api", "version": "0.1.0"}


@app.get("/health", tags=["health"])
async def health():
    return {"status": "healthy"}
