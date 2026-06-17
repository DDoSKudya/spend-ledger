import os

import pytest

pytestmark = pytest.mark.skipif(
    os.getenv("AUTH_INTEGRATION", "").lower() not in {"1", "true", "yes"},
    reason="Set AUTH_INTEGRATION=1 and AUTH_DATABASE_URL for auth integration tests",
)


@pytest.mark.asyncio
async def test_register_valid_credentials_returns_201(integration_client) -> None:
    """EC-P0 valid: new email + password -> 201."""
    response = await integration_client.post(
        "/internal/v1/auth/register",
        json={"email": "user@example.com", "password": "supersecret"},
    )
    assert response.status_code == 201
    assert response.json()["email"] == "user@example.com"


@pytest.mark.asyncio
async def test_login_valid_credentials_returns_tokens(integration_client) -> None:
    """EC-P0 valid: correct password -> access + refresh tokens."""
    client = integration_client
    await client.post(
        "/internal/v1/auth/register",
        json={"email": "login@example.com", "password": "supersecret"},
    )
    response = await client.post(
        "/internal/v1/auth/login",
        json={"email": "login@example.com", "password": "supersecret"},
    )
    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert "refresh_token" in body


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("email", "password"),
    [
        ("unknown@example.com", "supersecret"),
        ("login@example.com", "wrong-password"),
    ],
    ids=["unknown-user", "wrong-password"],
)
async def test_login_invalid_credentials_returns_401(
    integration_client,
    email: str,
    password: str,
) -> None:
    """EC-P0 invalid: unknown user or wrong password -> 401."""
    client = integration_client
    await client.post(
        "/internal/v1/auth/register",
        json={"email": "login@example.com", "password": "supersecret"},
    )
    response = await client.post(
        "/internal/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_verify_valid_access_token_returns_profile(integration_client) -> None:
    """EC-P0 valid: bearer access token -> user profile."""
    client = integration_client
    await client.post(
        "/internal/v1/auth/register",
        json={"email": "verify@example.com", "password": "supersecret"},
    )
    login = await client.post(
        "/internal/v1/auth/login",
        json={"email": "verify@example.com", "password": "supersecret"},
    )
    token = login.json()["access_token"]

    response = await client.get(
        "/internal/v1/auth/verify",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["email"] == "verify@example.com"


@pytest.mark.asyncio
async def test_refresh_rotates_token_and_invalidates_old(integration_client) -> None:
    """EC-P1: refresh returns new token; old refresh token is rejected."""
    client = integration_client
    await client.post(
        "/internal/v1/auth/register",
        json={"email": "rotate@example.com", "password": "supersecret"},
    )
    login = await client.post(
        "/internal/v1/auth/login",
        json={"email": "rotate@example.com", "password": "supersecret"},
    )
    tokens = login.json()

    refreshed = await client.post(
        "/internal/v1/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]},
    )
    assert refreshed.status_code == 200
    rotated = refreshed.json()
    assert rotated["refresh_token"] != tokens["refresh_token"]

    reused = await client.post(
        "/internal/v1/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]},
    )
    assert reused.status_code == 401


@pytest.mark.asyncio
async def test_logout_revokes_refresh_token(integration_client) -> None:
    """EC-P0: logout -> refresh token no longer accepted."""
    client = integration_client
    await client.post(
        "/internal/v1/auth/register",
        json={"email": "logout@example.com", "password": "supersecret"},
    )
    login = await client.post(
        "/internal/v1/auth/login",
        json={"email": "logout@example.com", "password": "supersecret"},
    )
    refresh_token = login.json()["refresh_token"]

    logout = await client.post(
        "/internal/v1/auth/logout",
        json={"refresh_token": refresh_token},
    )
    assert logout.status_code == 204

    reused = await client.post(
        "/internal/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert reused.status_code == 401
