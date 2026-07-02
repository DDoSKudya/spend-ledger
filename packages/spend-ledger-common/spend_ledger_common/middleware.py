import time
from collections.abc import Awaitable, Callable
from uuid import uuid4

import structlog
from fastapi import FastAPI, Request
from starlette.responses import Response

from spend_ledger_common.session import session_scope

REQUEST_ID_HEADER = "X-Request-Id"
DEFAULT_STATELESS_PATHS = frozenset({"/health", "/ready"})


def get_request_id(request: Request) -> str | None:
    return getattr(request.state, "request_id", None)


def register_request_id_middleware(app: FastAPI, *, service_name: str) -> None:
    @app.middleware("http")
    async def request_id_middleware(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        request_id = request.headers.get(REQUEST_ID_HEADER)
        if request_id is None:
            request_id = str(uuid4())
        request.state.request_id = request_id

        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id, service=service_name)
        try:
            response = await call_next(request)
            response.headers[REQUEST_ID_HEADER] = request_id
            return response
        finally:
            structlog.contextvars.clear_contextvars()


def register_request_log_middleware(app: FastAPI) -> None:
    @app.middleware("http")
    async def request_log_middleware(
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


def register_db_session_middleware(
    app: FastAPI,
    *,
    needs_session: Callable[[Request], bool] | None = None,
) -> None:
    def _default_needs_session(request: Request) -> bool:
        return request.url.path not in DEFAULT_STATELESS_PATHS

    predicate = needs_session or _default_needs_session

    @app.middleware("http")
    async def db_session_middleware(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        if not predicate(request):
            return await call_next(request)
        async with session_scope(request.app.state.session_factory):
            return await call_next(request)
