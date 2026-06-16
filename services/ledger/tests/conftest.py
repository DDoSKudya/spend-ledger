import os
from collections.abc import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

INTEGRATION = os.getenv("LEDGER_INTEGRATION", "").lower() in {"1", "true", "yes"}
TEST_USER_ID = "00000000-0000-4000-8000-000000000001"
TEST_USER_ID_B = "00000000-0000-4000-8000-000000000002"

if INTEGRATION:
    os.environ.setdefault(
        "LEDGER_DATABASE_URL",
        "postgresql+asyncpg://spend_ledger_test:test_ledger@localhost:5433/ledger_db_test",
    )
    os.environ["APP_ENV"] = "test"


@pytest.fixture
async def client() -> AsyncIterator[AsyncClient]:
    from app.main import app

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def engine():
    if not INTEGRATION:
        pytest.skip("LEDGER_INTEGRATION is not enabled")

    from app.core.models import Base

    url = os.environ["LEDGER_DATABASE_URL"]
    eng = create_async_engine(url)
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    try:
        yield eng
    finally:
        await eng.dispose()


@pytest.fixture
async def integration_client(engine) -> AsyncIterator[AsyncClient]:
    from app.core.deps import get_db
    from app.main import app

    session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async def override_get_db() -> AsyncIterator[AsyncSession]:
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    headers = {"X-User-Id": TEST_USER_ID}
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        headers=headers,
    ) as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture
async def integration_client_without_user_header(engine) -> AsyncIterator[AsyncClient]:
    from app.core.deps import get_db
    from app.main import app

    session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async def override_get_db() -> AsyncIterator[AsyncSession]:
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture
async def integration_client_user_b(engine) -> AsyncIterator[AsyncClient]:
    from app.core.deps import get_db
    from app.main import app

    session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async def override_get_db() -> AsyncIterator[AsyncSession]:
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    headers = {"X-User-Id": TEST_USER_ID_B}
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        headers=headers,
    ) as ac:
        yield ac
    app.dependency_overrides.clear()
