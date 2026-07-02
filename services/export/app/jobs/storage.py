from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

import redis

from app.jobs.schemas import ExportFilters, ExportFormat, JobRecord, JobStatus

JOB_KEY_PREFIX = "export:job:"
JOB_TTL_SECONDS = 60 * 60 * 24 * 7


def _new_pending_job(
    *,
    user_id: UUID,
    export_format: ExportFormat,
    filters: ExportFilters,
) -> JobRecord:
    return JobRecord(
        job_id=uuid4(),
        user_id=user_id,
        status=JobStatus.PENDING,
        format=export_format,
        filters=filters,
        created_at=datetime.now(UTC),
    )


class JobStoreBase:
    def create(
        self,
        *,
        user_id: UUID,
        export_format: ExportFormat,
        filters: ExportFilters,
    ) -> JobRecord:
        record = _new_pending_job(
            user_id=user_id,
            export_format=export_format,
            filters=filters,
        )
        self._write(record)
        return record

    def mark_processing(self, job_id: UUID) -> JobRecord | None:
        return self._update(job_id, status=JobStatus.PROCESSING)

    def mark_done(self, job_id: UUID, file_path: str) -> JobRecord | None:
        return self._update(
            job_id,
            status=JobStatus.DONE,
            file_path=file_path,
            completed_at=datetime.now(UTC),
            error_message=None,
        )

    def mark_failed(self, job_id: UUID, error_message: str) -> JobRecord | None:
        return self._update(
            job_id,
            status=JobStatus.FAILED,
            completed_at=datetime.now(UTC),
            error_message=error_message,
        )

    def _update(self, job_id: UUID, **changes: Any) -> JobRecord | None:
        record = self.get(job_id)
        if record is None:
            return None
        updated = record.model_copy(update=changes)
        self._write(updated)
        return updated

    def get(self, job_id: UUID) -> JobRecord | None:
        raise NotImplementedError

    def _write(self, record: JobRecord) -> None:
        raise NotImplementedError


class JobStore(JobStoreBase):
    def __init__(self, redis_url: str) -> None:
        self._redis = redis.from_url(redis_url, decode_responses=True)

    def close(self) -> None:
        self._redis.close()

    def ping(self) -> bool:
        try:
            return bool(self._redis.ping())
        except redis.RedisError:
            return False

    def get(self, job_id: UUID) -> JobRecord | None:
        raw = self._redis.get(_job_key(job_id))
        return None if raw is None else JobRecord.model_validate_json(str(raw))

    def _write(self, record: JobRecord) -> None:
        self._redis.setex(
            _job_key(record.job_id),
            JOB_TTL_SECONDS,
            record.model_dump_json(),
        )


def _job_key(job_id: UUID) -> str:
    return f"{JOB_KEY_PREFIX}{job_id}"
