import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_smoke(client: AsyncClient) -> None:
    """EC-P0: service is up."""
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
