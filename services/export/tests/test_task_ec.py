from pathlib import Path
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from app.jobs.schemas import ExportFilters, ExportFormat, JobStatus
from app.jobs.task import _run_export

# sourcery skip: dont-import-test-modules
from tests.memory_store import InMemoryJobStore

USER_ID = uuid4()


def test_run_export_happy_path_marks_job_done(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """EC-P0 valid: ledger rows -> done status + file on disk."""
    monkeypatch.setattr("app.jobs.task.settings.EXPORT_FILES_DIR", str(tmp_path))
    store = InMemoryJobStore()
    record = store.create(
        user_id=USER_ID,
        export_format=ExportFormat.CSV,
        filters=ExportFilters(),
    )

    ledger = MagicMock()
    ledger.iter_expenses.return_value = [
        {
            "id": str(uuid4()),
            "amount": "5.00",
            "category": {"name": "Travel"},
            "tags": [],
            "description": None,
            "expense_date": "2026-06-02",
            "created_at": "2026-06-02T10:00:00+00:00",
        }
    ]

    _run_export(
        store=store,
        ledger=ledger,
        job_id=record.job_id,
        user_id=USER_ID,
        filters=ExportFilters(),
        export_format=ExportFormat.CSV,
    )

    updated = store.get(record.job_id)
    assert updated is not None
    assert updated.status == JobStatus.DONE
    assert updated.file_path is not None
    assert Path(updated.file_path).is_file()


def test_run_export_idempotent_when_file_exists(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """EC-P1 valid: existing output file -> skip rewrite."""
    monkeypatch.setattr("app.jobs.task.settings.EXPORT_FILES_DIR", str(tmp_path))
    store = InMemoryJobStore()
    record = store.create(
        user_id=USER_ID,
        export_format=ExportFormat.CSV,
        filters=ExportFilters(),
    )

    file_path = tmp_path / str(USER_ID) / f"{record.job_id}.csv"
    file_path.parent.mkdir(parents=True)
    file_path.write_text("existing", encoding="utf-8")
    store.mark_done(record.job_id, str(file_path))

    ledger = MagicMock()
    ledger.iter_expenses.return_value = []

    _run_export(
        store=store,
        ledger=ledger,
        job_id=record.job_id,
        user_id=USER_ID,
        filters=ExportFilters(),
        export_format=ExportFormat.CSV,
    )

    ledger.iter_expenses.assert_not_called()
    assert file_path.read_text(encoding="utf-8") == "existing"
