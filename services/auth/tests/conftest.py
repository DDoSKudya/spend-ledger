import os
from collections.abc import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

INTEGRATION = os.getenv("AUTH_INTEGRATION", "").lower() in {"1", "true", "yes"}

if INTEGRATION:
    os.environ.setdefault(
        "AUTH_DATABASE_URL",
        "postgresql+asyncpg://spend_auth_test:test_auth@localhost:5434/auth_db_test",
    )
    os.environ["APP_ENV"] = "test"


@pytest.fixture
async def client() -> AsyncIterator[AsyncClient]:
    from app.main import app

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def integration_client() -> AsyncIterator[AsyncClient]:
    if not INTEGRATION:
        pytest.skip("AUTH_INTEGRATION is not enabled")

    from app.core.models import Base
    from app.main import app

    engine = create_async_engine(os.environ["AUTH_DATABASE_URL"])
    app.state.session_factory = async_sessionmaker(
        engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    await engine.dispose()
