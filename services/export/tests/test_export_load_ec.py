from pathlib import Path

from app.jobs.schemas import ExportFormat
from app.jobs.writer import write_export_file

LARGE_DATASET_SIZE = 1200


def _make_row(index: int) -> dict[str, object]:
    return {
        "id": f"{index:032x}",
        "amount": "10.00",
        "category": {"name": "Food"},
        "tags": [{"name": "weekly"}],
        "description": f"Expense {index}",
        "expense_date": "2026-06-01",
        "created_at": "2026-06-01T12:00:00+00:00",
    }


def test_write_csv_handles_large_dataset_without_error(tmp_path: Path) -> None:
    """EC-P2 load: 1200 rows export without failure."""
    rows = [_make_row(index) for index in range(LARGE_DATASET_SIZE)]
    path = tmp_path / "large.csv"

    write_export_file(path, ExportFormat.CSV, rows)

    assert path.is_file()
    assert path.stat().st_size > 0
    content = path.read_text(encoding="utf-8-sig")
    assert content.count("\n") >= LARGE_DATASET_SIZE
