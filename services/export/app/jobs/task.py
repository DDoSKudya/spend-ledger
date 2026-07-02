from pathlib import Path
from uuid import UUID

import structlog
from celery import Celery
from celery.signals import worker_process_init

from app.clients.ledger_client import LedgerClient
from app.core.config import settings
from app.jobs.schemas import ExportFilters, ExportFormat
from app.jobs.storage import JobStore, JobStoreBase
from app.jobs.writer import write_export_file
from spend_ledger_common.logging import setup_logging

logger = structlog.get_logger()

EXPORT_TASK_NAME = "export_expenses"

celery_app = Celery(
    "export",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)
celery_app.conf.update(
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)


@worker_process_init.connect
def _configure_worker_logging(**_kwargs) -> None:
    setup_logging(settings.LOG_LEVEL)


@celery_app.task(
    bind=True,
    name=EXPORT_TASK_NAME,
    max_retries=3,
    default_retry_delay=60,
    time_limit=600,
    soft_time_limit=540,
)
def export_expenses(
    self,
    job_id: str,
    user_id: str,
    filters: dict[str, object],
    export_format: str,
    request_id: str | None = None,
) -> None:
    structlog.contextvars.clear_contextvars()
    if request_id:
        structlog.contextvars.bind_contextvars(request_id=request_id, service="export-worker")

    store = JobStore(settings.REDIS_URL)
    ledger = LedgerClient(settings.LEDGER_SERVICE_URL)
    try:
        _run_export(
            store=store,
            ledger=ledger,
            job_id=UUID(job_id),
            user_id=UUID(user_id),
            filters=ExportFilters.model_validate(filters),
            export_format=ExportFormat(export_format),
            request_id=request_id,
        )
    except Exception as exc:
        logger.exception("export_job_failed", job_id=job_id, error=str(exc))
        if self.request.retries >= self.max_retries:
            store.mark_failed(UUID(job_id), str(exc))
            raise
        raise self.retry(exc=exc) from exc
    finally:
        structlog.contextvars.clear_contextvars()
        store.close()
        ledger.close()


def _run_export(
    *,
    store: JobStoreBase,
    ledger: LedgerClient,
    job_id: UUID,
    user_id: UUID,
    filters: ExportFilters,
    export_format: ExportFormat,
    request_id: str | None = None,
) -> None:
    record = store.get(job_id)
    if record is None:
        raise RuntimeError(f"Export job {job_id} not found")

    if record.is_ready and record.file_path is not None and Path(record.file_path).is_file():
        logger.info("export_job_idempotent_skip", job_id=str(job_id))
        return

    store.mark_processing(job_id)
    rows = ledger.iter_expenses(user_id, filters, request_id=request_id)
    file_path = _build_file_path(user_id, job_id, export_format)
    tmp_path = file_path.with_suffix(f"{file_path.suffix}.tmp")
    write_export_file(tmp_path, export_format, rows)
    tmp_path.replace(file_path)
    store.mark_done(job_id, str(file_path))
    logger.info("export_job_completed", job_id=str(job_id))


def _build_file_path(user_id: UUID, job_id: UUID, export_format: ExportFormat) -> Path:
    return Path(settings.EXPORT_FILES_DIR) / str(user_id) / f"{job_id}.{export_format.value}"
