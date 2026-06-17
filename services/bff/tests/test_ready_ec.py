import httpx
import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_ready_upstream_connection_error_returns_service_unavailable() -> None:
    """EC-P0 invalid: upstream connection failure -> 503."""

    class FailingClient:
        async def get(self, url: str, timeout: float = 5.0) -> None:
            raise httpx.ConnectError("connection refused", request=httpx.Request("GET", url))

    app.state.http_client = FailingClient()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/ready")

    assert response.status_code == 503
    assert response.json()["code"] == "service_unavailable"


@pytest.mark.asyncio
async def test_ready_upstream_non_200_returns_service_unavailable() -> None:
    """EC-P0 invalid: upstream not ready -> 503 with code."""

    class FakeResponse:
        status_code = 503

    class FakeClient:
        async def get(self, url: str, timeout: float = 5.0) -> FakeResponse:
            return FakeResponse()

    app.state.http_client = FakeClient()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/ready")

    assert response.status_code == 503
    body = response.json()
    assert body["code"] == "service_unavailable"
    assert "service is not ready" in body["detail"]
