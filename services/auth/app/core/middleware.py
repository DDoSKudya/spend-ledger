import time
from collections.abc import Awaitable, Callable
from uuid import uuid4

import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.session import session_scope

SERVICE_NAME = "auth"
_STATELESS_PATHS = frozenset({"/health", "/ready"})


def _needs_db_session(request: Request) -> bool:
    if request.url.path in _STATELESS_PATHS:
        return False
    if request.url.path == "/internal/v1/auth/verify":
        authorization = request.headers.get("Authorization", "")
        return authorization.startswith("Bearer ")
    return True


class DbSessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        if not _needs_db_session(request):
            return await call_next(request)
        async with session_scope(request.app.state.session_factory):
            return await call_next(request)


class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        request_id = request.headers.get("X-Request-Id", str(uuid4()))
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id, service=SERVICE_NAME)
        response = await call_next(request)
        response.headers["X-Request-Id"] = request_id
        return response


class RequestLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        started = time.perf_counter()
        response = await call_next(request)
        duration_ms = round((time.perf_counter() - started) * 1000, 2)
        structlog.get_logger().info(
            "request_completed",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=duration_ms,
        )
        return response
