from pathlib import Path
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from app.jobs.schemas import ExportFilters, ExportFormat, JobStatus
from app.jobs.task import _run_export

# sourcery skip: dont-import-test-modules
from tests.memory_store import InMemoryJobStore

USER_ID = uuid4()


def test_run_export_writes_csv_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
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
