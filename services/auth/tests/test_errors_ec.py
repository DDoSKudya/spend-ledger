import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_verify_missing_bearer_returns_error_code(integration_client: AsyncClient) -> None:
    """EC-P0 invalid: missing bearer token -> 401 with code."""
    response = await integration_client.get("/internal/v1/auth/verify")

    assert response.status_code == 401
    body = response.json()
    assert body["code"] == "missing_bearer_token"
    assert body["detail"] == "Missing bearer token"
