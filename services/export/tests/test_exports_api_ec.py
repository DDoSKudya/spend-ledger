from unittest.mock import patch
from uuid import UUID, uuid4

import pytest
from httpx import AsyncClient

from tests.conftest import USER_ID
from tests.memory_store import InMemoryJobStore


@pytest.mark.asyncio
async def test_create_export_valid_request_returns_202(
    client: AsyncClient,
    user_headers: dict[str, str],
) -> None:
    """EC-P0 valid: authenticated create -> 202 pending job."""
    with patch("app.jobs.service.celery_app.send_task") as send_task:
        response = await client.post(
            "/internal/v1/exports",
            headers=user_headers,
            json={"format": "csv", "filters": {"date_from": "2026-01-01"}},
        )

    assert response.status_code == 202
    payload = response.json()
    assert payload["status"] == "pending"
    assert payload["format"] == "csv"
    send_task.assert_called_once()


@pytest.mark.asyncio
async def test_create_export_missing_user_header_returns_401(client: AsyncClient) -> None:
    """EC-P0 invalid: missing X-User-Id -> 401."""
    response = await client.post("/internal/v1/exports", json={"format": "csv"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_own_job_returns_status(
    client: AsyncClient,
    user_headers: dict[str, str],
) -> None:
    """EC-P0 valid: owner can read job status."""
    with patch("app.jobs.service.celery_app.send_task"):
        created = await client.post(
            "/internal/v1/exports",
            headers=user_headers,
            json={"format": "csv"},
        )
    job_id = created.json()["job_id"]

    response = await client.get(f"/internal/v1/exports/{job_id}", headers=user_headers)
    assert response.status_code == 200
    assert response.json()["job_id"] == job_id


@pytest.mark.asyncio
async def test_get_foreign_job_returns_404(
    client: AsyncClient,
    user_headers: dict[str, str],
) -> None:
    """EC-P0 invalid: foreign job id -> 404."""
    foreign_job_id = uuid4()
    response = await client.get(
        f"/internal/v1/exports/{foreign_job_id}",
        headers=user_headers,
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_ready_when_store_unavailable_returns_503(
    client: AsyncClient,
    job_store: InMemoryJobStore,
) -> None:
    """EC-P0 invalid: Redis down -> 503 service_unavailable."""
    job_store.set_available(False)
    response = await client.get("/ready")
    assert response.status_code == 503
    assert response.json()["code"] == "service_unavailable"


@pytest.mark.asyncio
async def test_download_ready_export_returns_file(
    client: AsyncClient,
    user_headers: dict[str, str],
    job_store: InMemoryJobStore,
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """EC-P0 valid: completed job file is downloadable."""
    monkeypatch.setattr("app.jobs.service.settings.EXPORT_FILES_DIR", str(tmp_path))
    with patch("app.jobs.service.celery_app.send_task"):
        created = await client.post(
            "/internal/v1/exports",
            headers=user_headers,
            json={"format": "csv"},
        )
    job_id = created.json()["job_id"]

    file_path = tmp_path / str(USER_ID) / f"{job_id}.csv"
    file_path.parent.mkdir(parents=True)
    file_path.write_text("id,amount\n", encoding="utf-8")
    job_store.mark_done(UUID(job_id), str(file_path))

    response = await client.get(
        f"/internal/v1/exports/{job_id}/file",
        headers=user_headers,
    )
    assert response.status_code == 200
    assert "text/csv" in response.headers.get("content-type", "")


@pytest.mark.asyncio
async def test_get_failed_job_returns_failed_status(
    client: AsyncClient,
    user_headers: dict[str, str],
    job_store: InMemoryJobStore,
) -> None:
    """EC-P0 valid: failed job exposes error_message."""
    with patch("app.jobs.service.celery_app.send_task"):
        created = await client.post(
            "/internal/v1/exports",
            headers=user_headers,
            json={"format": "csv"},
        )
    job_id = UUID(created.json()["job_id"])
    job_store.mark_failed(job_id, "ledger timeout")

    response = await client.get(f"/internal/v1/exports/{job_id}", headers=user_headers)
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "failed"
    assert payload["error_message"] == "ledger timeout"
