import csv
from datetime import date
from pathlib import Path
from uuid import UUID

import pytest

from app.jobs.schemas import ExportFilters, ExportFormat
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


@pytest.mark.parametrize(
    "export_format", [ExportFormat.CSV, ExportFormat.XLSX], ids=["csv", "xlsx"]
)
def test_write_export_valid_format_creates_file(
    tmp_path: Path,
    export_format: ExportFormat,
) -> None:
    """EC-P0 valid: supported format -> non-empty file."""
    path = tmp_path / f"export.{export_format.value}"
    write_export_file(path, export_format, SAMPLE_ROWS)
    assert path.is_file()
    assert path.stat().st_size > 0


def test_write_csv_maps_row_fields(tmp_path: Path) -> None:
    """EC-P0 valid: CSV row preserves business fields."""
    path = tmp_path / "export.csv"
    write_export_file(path, ExportFormat.CSV, SAMPLE_ROWS)

    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))

    assert rows[0]["category"] == "Food"
    assert rows[0]["tags"] == "groceries"
    assert rows[0]["amount"] == "10.50"


def test_write_csv_empty_rows_writes_header_only(tmp_path: Path) -> None:
    # sourcery skip: simplify-empty-collection-comparison
    """EC-P0 boundary: empty list -> header row only."""
    path = tmp_path / "empty.csv"
    write_export_file(path, ExportFormat.CSV, [])

    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))

    assert rows == []


def test_export_filters_to_query_params_includes_optional_fields() -> None:
    """EC-P1 valid: optional filters are serialized to query params."""
    category_id = UUID("11111111-1111-1111-1111-111111111111")
    tag_id = UUID("22222222-2222-2222-2222-222222222222")
    filters = ExportFilters(
        category_id=category_id,
        tag_ids=[tag_id],
        date_from=date(2026, 1, 1),
        date_to=date(2026, 6, 30),
        search="coffee",
    )

    params = filters.to_query_params(page=2, size=50)

    assert params == {
        "page": 2,
        "size": 50,
        "sort": "expense_date:desc",
        "category_id": str(category_id),
        "tag_ids": [str(tag_id)],
        "date_from": "2026-01-01",
        "date_to": "2026-06-30",
        "search": "coffee",
    }
