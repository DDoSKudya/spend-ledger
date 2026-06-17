import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("method", "path", "json_body"),
    [
        ("GET", "/api/v1/categories", None),
        ("GET", "/api/v1/reports/monthly", None),
        ("POST", "/api/v1/exports", {"format": "csv"}),
    ],
    ids=["categories", "reports", "exports"],
)
async def test_protected_route_without_bearer_returns_401(
    client: AsyncClient,
    method: str,
    path: str,
    json_body: dict | None,
) -> None:
    """EC-P0 invalid auth: missing bearer token -> 401 unauthorized."""
    response = await client.request(method, path, json=json_body)
    assert response.status_code == 401
    assert response.json()["code"] == "missing_bearer_token"


@pytest.mark.asyncio
async def test_protected_route_with_invalid_bearer_returns_401(client: AsyncClient) -> None:
    """EC-P0 invalid auth: malformed token -> 401 invalid_token."""
    response = await client.get(
        "/api/v1/categories",
        headers={"Authorization": "Bearer not-a-jwt"},
    )
    assert response.status_code == 401
    assert response.json()["code"] == "invalid_token"
