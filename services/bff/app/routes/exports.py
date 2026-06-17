import json

from fastapi import APIRouter, Request, Response
from fastapi.responses import JSONResponse

from app.clients.proxy import forward_to_export
from app.core.constants import HTTP_OK
from app.core.exceptions import InvalidUpstreamResponseError

router = APIRouter(prefix="/api/v1/exports", tags=["exports"])

EXPORT_STATUS_DONE = "done"


@router.post("")
async def create_export(request: Request) -> Response:
    return await forward_to_export(request, "/internal/v1/exports")


@router.get("/{job_id}")
async def get_export_status(request: Request, job_id: str) -> Response:
    response = await forward_to_export(request, f"/internal/v1/exports/{job_id}")
    if response.status_code != HTTP_OK:
        return response

    try:
        payload = json.loads(bytes(response.body))
    except json.JSONDecodeError as exc:
        raise InvalidUpstreamResponseError() from exc

    if payload.get("status") == EXPORT_STATUS_DONE:
        payload["download_url"] = f"/api/v1/exports/{job_id}/download"
    return JSONResponse(content=payload, status_code=response.status_code)


@router.get("/{job_id}/download")
async def download_export(request: Request, job_id: str) -> Response:
    return await forward_to_export(request, f"/internal/v1/exports/{job_id}/file")
