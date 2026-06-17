from collections.abc import AsyncIterator
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

# sourcery skip: dont-import-test-modules
from tests.memory_store import InMemoryJobStore

from app.main import app

USER_ID = uuid4()


@pytest.fixture
def job_store() -> InMemoryJobStore:
    return InMemoryJobStore()


@pytest.fixture
async def client(job_store: InMemoryJobStore) -> AsyncIterator[AsyncClient]:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        app.state.job_store = job_store
        yield ac


@pytest.fixture
def user_headers() -> dict[str, str]:
    return {"X-User-Id": str(USER_ID)}
