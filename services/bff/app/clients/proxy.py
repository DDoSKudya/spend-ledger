import json

from fastapi import Request, Response
from httpx import AsyncClient, HTTPError

from app.core.config import settings
from app.core.exceptions import InvalidUpstreamResponseError
from spend_ledger_common.constants import default_http_error_code
from spend_ledger_common.middleware import get_request_id

FORWARD_REQUEST_HEADERS = frozenset({"accept", "authorization", "content-type"})


def _normalize_error_body(status_code: int, content: bytes, content_type: str | None) -> bytes:
    if status_code < 400:
        return content

    fallback = json.dumps(
        {"detail": "Upstream error", "code": default_http_error_code(status_code)},
    ).encode()

    if not content_type or "application/json" not in content_type.lower():
        return fallback

    try:
        body = json.loads(content)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return fallback

    if not isinstance(body, dict):
        return fallback

    if "detail" in body and "code" in body:
        return content

    detail = body.get("detail", "Upstream error")
    if not isinstance(detail, str):
        detail = str(detail)

    normalized: dict[str, object] = {
        "detail": detail,
        "code": body.get("code", default_http_error_code(status_code)),
    }
    if "errors" in body:
        normalized["errors"] = body["errors"]
    return json.dumps(normalized).encode()


def _build_headers(request: Request) -> dict[str, str]:
    headers: dict[str, str] = {}
    request_id = get_request_id(request)
    if request_id:
        headers["X-Request-Id"] = request_id

    for name, value in request.headers.items():
        if name.lower() in FORWARD_REQUEST_HEADERS:
            headers[name] = value

    user_id = getattr(request.state, "user_id", None)
    if user_id is not None:
        headers["X-User-Id"] = str(user_id)

    return headers


def _to_response(upstream) -> Response:
    content_type = upstream.headers.get("content-type")
    content = _normalize_error_body(upstream.status_code, upstream.content, content_type)

    response_headers: dict[str, str] = {}
    if content_type:
        response_headers["content-type"] = content_type
    content_disposition = upstream.headers.get("content-disposition")
    if content_disposition:
        response_headers["content-disposition"] = content_disposition
    return Response(
        content=content,
        status_code=upstream.status_code,
        headers=response_headers,
    )


async def _upstream_request(client: AsyncClient, method: str, url: str, **kwargs) -> Response:
    try:
        upstream = await client.request(method, url, **kwargs)
    except HTTPError as exc:
        raise InvalidUpstreamResponseError("Upstream service is unreachable") from exc
    return _to_response(upstream)


async def forward_to_ledger(request: Request, path: str) -> Response:
    client: AsyncClient = request.app.state.http_client
    headers = _build_headers(request)
    body = await request.body()
    return await _upstream_request(
        client,
        request.method,
        f"{settings.LEDGER_SERVICE_URL}{path}",
        params=list(request.query_params.multi_items()),
        content=body or None,
        headers=headers,
    )


async def forward_to_export(request: Request, path: str) -> Response:
    client: AsyncClient = request.app.state.http_client
    headers = _build_headers(request)
    body = await request.body()
    return await _upstream_request(
        client,
        request.method,
        f"{settings.EXPORT_SERVICE_URL}{path}",
        params=list(request.query_params.multi_items()),
        content=body or None,
        headers=headers,
    )


async def forward_to_auth(
    request: Request,
    path: str,
    json_body: dict[str, object] | None = None,
) -> Response:
    client: AsyncClient = request.app.state.http_client
    headers = _build_headers(request)
    return await _upstream_request(
        client,
        request.method,
        f"{settings.AUTH_SERVICE_URL}{path}",
        json=json_body,
        headers=headers,
    )
