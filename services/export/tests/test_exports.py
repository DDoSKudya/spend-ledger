import csv
from pathlib import Path
from unittest.mock import patch
from uuid import uuid4

import pytest
from httpx import AsyncClient

from app.jobs.schemas import ExportFormat
from app.jobs.writer import write_export_file

SAMPLE_ROWS = [
    {
        "id": "11111111-1111-1111-1111-111111111111",
        "amount": "10.50",
        "category": {"name": "Food"},
        "tags": [{"name": "groceries"}],
        "description": "Lunch",
        "expense_date": "2026-06-01",
        "created_at": "2026-06-01T12:00:00+00:00",
    }
]


def test_write_csv_contains_headers_and_row(tmp_path: Path) -> None:
    path = tmp_path / "export.csv"
    write_export_file(path, ExportFormat.CSV, SAMPLE_ROWS)

    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))

    assert rows[0]["category"] == "Food"
    assert rows[0]["tags"] == "groceries"
    assert rows[0]["amount"] == "10.50"


def test_write_xlsx_creates_file(tmp_path: Path) -> None:
    path = tmp_path / "export.xlsx"
    write_export_file(path, ExportFormat.XLSX, SAMPLE_ROWS)
    assert path.is_file()
    assert path.stat().st_size > 0


@pytest.mark.asyncio
async def test_create_export_returns_202(
    client: AsyncClient,
    user_headers: dict[str, str],
) -> None:
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
async def test_create_export_requires_user_header(client: AsyncClient) -> None:
    response = await client.post("/internal/v1/exports", json={"format": "csv"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_export_job_returns_status(
    client: AsyncClient,
    user_headers: dict[str, str],
) -> None:
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
    foreign_job_id = uuid4()
    response = await client.get(
        f"/internal/v1/exports/{foreign_job_id}",
        headers=user_headers,
    )
    assert response.status_code == 404
