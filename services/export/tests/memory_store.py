from uuid import UUID

from app.jobs.schemas import JobRecord
from app.jobs.storage import JobStoreBase


class InMemoryJobStore(JobStoreBase):
    def __init__(self) -> None:
        self._jobs: dict[UUID, JobRecord] = {}
        self._available = True

    def close(self) -> None:
        return None

    def ping(self) -> bool:
        return self._available

    def set_available(self, available: bool) -> None:
        self._available = available

    def get(self, job_id: UUID) -> JobRecord | None:
        return self._jobs.get(job_id)

    def _write(self, record: JobRecord) -> None:
        self._jobs[record.job_id] = record
