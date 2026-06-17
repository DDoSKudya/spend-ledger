from uuid import UUID

from fastapi import APIRouter, Request, status
from fastapi.responses import FileResponse

from app.core.deps import CurrentUserId
from app.jobs import service
from app.jobs.schemas import EXPORT_MEDIA_TYPES, ExportCreate, ExportJobRead
from app.jobs.storage import JobStoreProtocol

router = APIRouter(prefix="/internal/v1/exports", tags=["exports"])


def _store(request: Request) -> JobStoreProtocol:
    return request.app.state.job_store


@router.post("", response_model=ExportJobRead, status_code=status.HTTP_202_ACCEPTED)
async def create_export(
    data: ExportCreate,
    user_id: CurrentUserId,
    request: Request,
) -> ExportJobRead:
    return service.create_export_job(_store(request), user_id, data)


@router.get("/{job_id}", response_model=ExportJobRead)
async def get_export(job_id: UUID, user_id: CurrentUserId, request: Request) -> ExportJobRead:
    return service.get_export_job(_store(request), user_id, job_id)


@router.get("/{job_id}/file")
async def download_export(job_id: UUID, user_id: CurrentUserId, request: Request) -> FileResponse:
    file_path, export_format = service.resolve_export_file(_store(request), user_id, job_id)
    return FileResponse(
        path=file_path,
        media_type=EXPORT_MEDIA_TYPES[export_format.value],
        filename=file_path.name,
    )
