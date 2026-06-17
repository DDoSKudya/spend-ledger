import json
from uuid import uuid4

import jwt
import pytest
from httpx import ASGITransport, AsyncClient
from starlette.responses import Response

from app.core.config import settings


def _auth_headers() -> dict[str, str]:
    token = jwt.encode(
        {"sub": str(uuid4()), "type": "access"},
        settings.JWT_SECRET,
        algorithm="HS256",
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_get_export_status_invalid_upstream_json_returns_502(monkeypatch) -> None:
    """EC-P0 invalid: malformed export status body -> 502 with code."""
    from app.main import app

    async def fake_forward(_request, _path: str) -> Response:
        return Response(content=b"not-json", status_code=200, media_type="application/json")

    monkeypatch.setattr("app.routes.exports.forward_to_export", fake_forward)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(
            "/api/v1/exports/job-1",
            headers=_auth_headers(),
        )

    assert response.status_code == 502
    body = response.json()
    assert body["code"] == "invalid_upstream_response"


@pytest.mark.asyncio
async def test_get_export_status_done_adds_download_url(monkeypatch) -> None:
    """EC-P0 valid: done job gets download_url injected."""
    from app.main import app

    payload = {"job_id": "job-1", "status": "done", "format": "csv"}

    async def fake_forward(_request, _path: str) -> Response:
        return Response(
            content=json.dumps(payload).encode(),
            status_code=200,
            media_type="application/json",
        )

    monkeypatch.setattr("app.routes.exports.forward_to_export", fake_forward)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(
            "/api/v1/exports/job-1",
            headers=_auth_headers(),
        )

    assert response.status_code == 200
    body = response.json()
    assert body["download_url"] == "/api/v1/exports/job-1/download"
