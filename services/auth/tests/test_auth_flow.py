import os

import pytest

pytestmark = pytest.mark.skipif(
    os.getenv("AUTH_INTEGRATION", "").lower() not in {"1", "true", "yes"},
    reason="Set AUTH_INTEGRATION=1 and AUTH_DATABASE_URL for auth integration tests",
)


@pytest.mark.asyncio
async def test_register_login_verify(integration_client):
    client = integration_client
    register = await client.post(
        "/internal/v1/auth/register",
        json={"email": "user@example.com", "password": "supersecret"},
    )
    assert register.status_code == 201

    login = await client.post(
        "/internal/v1/auth/login",
        json={"email": "user@example.com", "password": "supersecret"},
    )
    assert login.status_code == 200
    tokens = login.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens

    verify = await client.get(
        "/internal/v1/auth/verify",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    assert verify.status_code == 200
    assert verify.json()["email"] == "user@example.com"

    refreshed = await client.post(
        "/internal/v1/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]},
    )
    assert refreshed.status_code == 200
    rotated_tokens = refreshed.json()
    assert rotated_tokens["refresh_token"] != tokens["refresh_token"]

    reused_old = await client.post(
        "/internal/v1/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]},
    )
    assert reused_old.status_code == 401

    logout = await client.post(
        "/internal/v1/auth/logout",
        json={"refresh_token": rotated_tokens["refresh_token"]},
    )
    assert logout.status_code == 204
