import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health(client: AsyncClient) -> None:
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_api_health(client: AsyncClient) -> None:
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "bff"}


@pytest.mark.asyncio
async def test_categories_requires_bearer_token(client: AsyncClient) -> None:
    response = await client.get("/api/v1/categories")
    assert response.status_code == 401
    assert response.json()["code"] == "unauthorized"


@pytest.mark.asyncio
async def test_reports_requires_bearer_token(client: AsyncClient) -> None:
    response = await client.get("/api/v1/reports/monthly")
    assert response.status_code == 401
    assert response.json()["code"] == "unauthorized"
