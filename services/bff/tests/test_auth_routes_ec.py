import pytest
from httpx import ASGITransport, AsyncClient


@pytest.mark.asyncio
async def test_refresh_without_cookie_returns_missing_refresh_token_code() -> None:
    """EC-P0 invalid: no refresh cookie -> 401 with code."""
    from app.main import app

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/v1/auth/refresh")

    assert response.status_code == 401
    body = response.json()
    assert body["code"] == "missing_refresh_token"
    assert body["detail"] == "Missing refresh token"


@pytest.mark.asyncio
async def test_me_without_bearer_returns_missing_bearer_token_code() -> None:
    """EC-P0 invalid: no Authorization header -> 401 with code."""
    from app.main import app

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/auth/me")

    assert response.status_code == 401
    body = response.json()
    assert body["code"] == "missing_bearer_token"
    assert body["detail"] == "Missing bearer token"
