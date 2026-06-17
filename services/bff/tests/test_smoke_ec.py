import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_smoke(client: AsyncClient) -> None:
    """EC-P0: service is up."""
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_api_health_smoke(client: AsyncClient) -> None:
    """EC-P0: public BFF health."""
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "bff"}
