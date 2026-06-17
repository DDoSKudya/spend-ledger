import json

from fastapi import APIRouter, Request, Response
from starlette import status
from starlette.responses import JSONResponse

from app.clients.proxy import forward_to_export

router = APIRouter(prefix="/api/v1/exports", tags=["exports"])

HTTP_OK = status.HTTP_200_OK
EXPORT_STATUS_DONE = "done"


@router.post("")
async def create_export(request: Request) -> Response:
    return await forward_to_export(request, "/internal/v1/exports")


@router.get("/{job_id}")
async def get_export_status(request: Request, job_id: str) -> Response:
    response = await forward_to_export(request, f"/internal/v1/exports/{job_id}")
    if response.status_code != HTTP_OK:
        return response

    payload = json.loads(bytes(response.body))
    if payload.get("status") == EXPORT_STATUS_DONE:
        payload["download_url"] = f"/api/v1/exports/{job_id}/download"
    return JSONResponse(content=payload, status_code=response.status_code)


@router.get("/{job_id}/download")
async def download_export(request: Request, job_id: str) -> Response:
    return await forward_to_export(request, f"/internal/v1/exports/{job_id}/file")
