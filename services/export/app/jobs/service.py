from pathlib import Path
from uuid import UUID

import structlog

from app.core.config import settings
from app.core.exceptions import NotFoundError
from app.jobs.schemas import ExportCreate, ExportFormat, ExportJobRead, JobRecord
from app.jobs.storage import JobStoreProtocol
from app.jobs.task import EXPORT_TASK_NAME, celery_app

logger = structlog.get_logger()


def _owned_job(store: JobStoreProtocol, job_id: UUID, user_id: UUID) -> JobRecord:
    record = store.get(job_id)
    if record is None or record.user_id != user_id:
        raise NotFoundError("export job")
    return record


def create_export_job(
    store: JobStoreProtocol,
    user_id: UUID,
    data: ExportCreate,
) -> ExportJobRead:
    record = store.create(
        user_id=user_id,
        export_format=data.format,
        filters=data.filters,
    )
    celery_app.send_task(
        EXPORT_TASK_NAME,
        args=[
            str(record.job_id),
            str(user_id),
            data.filters.model_dump(mode="json"),
            data.format.value,
        ],
    )
    logger.info("export_job_enqueued", job_id=str(record.job_id), format=data.format)
    return record.to_read_model()


def get_export_job(store: JobStoreProtocol, user_id: UUID, job_id: UUID) -> ExportJobRead:
    return _owned_job(store, job_id, user_id).to_read_model()


def resolve_export_file(
    store: JobStoreProtocol,
    user_id: UUID,
    job_id: UUID,
) -> tuple[Path, ExportFormat]:
    record = _owned_job(store, job_id, user_id)
    if not record.is_ready or record.file_path is None:
        raise NotFoundError("export file")

    file_path = Path(record.file_path).resolve()
    exports_root = Path(settings.EXPORT_FILES_DIR).resolve()
    if not file_path.is_relative_to(exports_root) or not file_path.is_file():
        raise NotFoundError("export file")
    return file_path, record.format
