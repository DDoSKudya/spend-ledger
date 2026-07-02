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
    from app.main import app

    app.state.session_factory = async_sessionmaker(
        engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )
    headers = {"X-User-Id": TEST_USER_ID}
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        headers=headers,
    ) as ac:
        yield ac


@pytest.fixture
async def integration_client_without_user_header(engine) -> AsyncIterator[AsyncClient]:
    from app.main import app

    app.state.session_factory = async_sessionmaker(
        engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def integration_client_user_b(engine) -> AsyncIterator[AsyncClient]:
    from app.main import app

    app.state.session_factory = async_sessionmaker(
        engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )
    headers = {"X-User-Id": TEST_USER_ID_B}
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        headers=headers,
    ) as ac:
        yield ac


@pytest.fixture
async def expense_dataset(integration_client):
    client = integration_client
    food = (await client.post("/internal/v1/categories", json={"name": "Food"})).json()
    transport = (await client.post("/internal/v1/categories", json={"name": "Transport"})).json()
    weekly = (await client.post("/internal/v1/tags", json={"name": "weekly"})).json()
    urgent = (await client.post("/internal/v1/tags", json={"name": "urgent"})).json()

    async def add_expense(**payload):
        response = await client.post("/internal/v1/expenses", json=payload)
        assert response.status_code == 201
        return response.json()

    groceries = await add_expense(
        amount="42.50",
        category_id=food["id"],
        tag_ids=[weekly["id"]],
        description="groceries",
        expense_date="2026-06-15",
    )
    taxi = await add_expense(
        amount="15.00",
        category_id=transport["id"],
        tag_ids=[urgent["id"]],
        description="taxi ride",
        expense_date="2026-06-20",
    )
    lunch = await add_expense(
        amount="8.00",
        category_id=food["id"],
        tag_ids=[weekly["id"], urgent["id"]],
        description="lunch",
        expense_date="2026-07-01",
    )

    return {
        "food_id": food["id"],
        "transport_id": transport["id"],
        "weekly_id": weekly["id"],
        "urgent_id": urgent["id"],
        "groceries_id": groceries["id"],
        "taxi_id": taxi["id"],
        "lunch_id": lunch["id"],
    }
