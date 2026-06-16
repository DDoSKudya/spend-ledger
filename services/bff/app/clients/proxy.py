from fastapi import Request, Response
from httpx import AsyncClient

from app.core.config import settings

FORWARD_REQUEST_HEADERS = frozenset({"accept", "authorization", "content-type"})


def _build_headers(request: Request) -> dict[str, str]:
    headers: dict[str, str] = {}
    request_id = request.headers.get("X-Request-Id")
    if request_id:
        headers["X-Request-Id"] = request_id

    for name, value in request.headers.items():
        if name.lower() in FORWARD_REQUEST_HEADERS:
            headers[name] = value

    return headers


async def forward_to_ledger(request: Request, path: str) -> Response:
    client: AsyncClient = request.app.state.http_client
    headers = _build_headers(request)
    user_id = getattr(request.state, "user_id", None)
    if user_id is not None:
        headers["X-User-Id"] = str(user_id)

    body = await request.body()
    upstream = await client.request(
        request.method,
        f"{settings.LEDGER_SERVICE_URL}{path}",
        params=list(request.query_params.multi_items()),
        content=body or None,
        headers=headers,
    )
    response_headers: dict[str, str] = {}
    content_type = upstream.headers.get("content-type")
    if content_type:
        response_headers["content-type"] = content_type
    return Response(
        content=upstream.content,
        status_code=upstream.status_code,
        headers=response_headers,
    )


async def forward_to_auth(
    request: Request,
    path: str,
    json_body: dict[str, object] | None = None,
) -> Response:
    client: AsyncClient = request.app.state.http_client
    headers = _build_headers(request)

    upstream = await client.request(
        request.method,
        f"{settings.AUTH_SERVICE_URL}{path}",
        json=json_body,
        headers=headers,
    )
    response_headers: dict[str, str] = {}
    content_type = upstream.headers.get("content-type")
    if content_type:
        response_headers["content-type"] = content_type
    return Response(
        content=upstream.content,
        status_code=upstream.status_code,
        headers=response_headers,
    )
