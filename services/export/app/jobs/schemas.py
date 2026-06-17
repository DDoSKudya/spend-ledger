from datetime import date, datetime
from enum import StrEnum
from typing import Final
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

EXPORT_MEDIA_TYPES: Final[dict[str, str]] = {
    "csv": "text/csv",
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}


class ExportFormat(StrEnum):
    CSV = "csv"
    XLSX = "xlsx"


class JobStatus(StrEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    DONE = "done"
    FAILED = "failed"


class ExportFilters(BaseModel):
    category_id: UUID | None = None
    tag_ids: list[UUID] = Field(default_factory=list)
    date_from: date | None = None
    date_to: date | None = None
    search: str | None = None
    sort: str = "expense_date:desc"

    def to_query_params(
        self,
        *,
        page: int,
        size: int,
    ) -> dict[str, str | int | list[str]]:
        params: dict[str, str | int | list[str]] = {
            "page": page,
            "size": size,
            "sort": self.sort,
        }
        if self.category_id is not None:
            params["category_id"] = str(self.category_id)
        if self.tag_ids:
            params["tag_ids"] = [str(tag_id) for tag_id in self.tag_ids]
        if self.date_from is not None:
            params["date_from"] = self.date_from.isoformat()
        if self.date_to is not None:
            params["date_to"] = self.date_to.isoformat()
        if self.search:
            params["search"] = self.search
        return params


class ExportCreate(BaseModel):
    format: ExportFormat
    filters: ExportFilters = Field(default_factory=ExportFilters)


class ExportJobRead(BaseModel):
    job_id: UUID
    status: JobStatus
    format: ExportFormat
    created_at: datetime
    completed_at: datetime | None = None
    error_message: str | None = None
    download_url: str | None = None


class JobRecord(BaseModel):
    model_config = ConfigDict(frozen=True)

    job_id: UUID
    user_id: UUID
    status: JobStatus
    format: ExportFormat
    filters: ExportFilters
    file_path: str | None = None
    error_message: str | None = None
    created_at: datetime
    completed_at: datetime | None = None

    @property
    def is_ready(self) -> bool:
        return self.status == JobStatus.DONE and self.file_path is not None

    def to_read_model(self) -> ExportJobRead:
        download_url = f"/internal/v1/exports/{self.job_id}/file" if self.is_ready else None
        return ExportJobRead(
            job_id=self.job_id,
            status=self.status,
            format=self.format,
            created_at=self.created_at,
            completed_at=self.completed_at,
            error_message=self.error_message,
            download_url=download_url,
        )
