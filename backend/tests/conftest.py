"""
Pytest configuration and shared fixtures for Lighthouse backend tests.

Defaults to an in-memory SQLite database for fast local runs.
Set TEST_DATABASE_URL in the environment to target PostgreSQL instead
(used in CI where a Postgres service is already running).
"""
import os
from typing import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool, StaticPool

from app.database import Base, get_db
from app.main import app

# ---------------------------------------------------------------------------
# CI passes TEST_DATABASE_URL pointing at the Postgres service container.
# Local runs default to SQLite in-memory (no Docker needed for unit tests).
# ---------------------------------------------------------------------------
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "sqlite+aiosqlite:///:memory:")

# SQLite in-memory: use StaticPool so all connections share the same database.
# PostgreSQL: use NullPool to prevent the session-scoped engine from holding
# loop-bound connections, which would cause "Future attached to a different loop"
# when function-scoped tests run in their own event loops.
if TEST_DATABASE_URL.startswith("sqlite"):
    _pool_kwargs = {"poolclass": StaticPool, "connect_args": {"check_same_thread": False}}
else:
    _pool_kwargs = {"poolclass": NullPool}


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def engine():
    _engine = create_async_engine(TEST_DATABASE_URL, echo=False, **_pool_kwargs)
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield _engine
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await _engine.dispose()


@pytest_asyncio.fixture()
async def db_session(engine) -> AsyncGenerator[AsyncSession, None]:
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture()
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """HTTP test client with the DB dependency overridden to use the test session."""

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()
