import time
from collections.abc import Awaitable, Callable
from uuid import uuid4

import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.config import settings
from app.core.deps import get_sql_count, reset_sql_count

SERVICE_NAME = "ledger"
HIGH_SQL_QUERY_THRESHOLD = 10


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


class SqlProfileMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        if settings.PROFILE_REQUESTS:
            reset_sql_count()
        started = time.perf_counter()
        response = await call_next(request)
        duration_ms = round((time.perf_counter() - started) * 1000, 2)
        log_kwargs: dict[str, object] = {
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": duration_ms,
        }
        if settings.PROFILE_REQUESTS:
            sql_queries = get_sql_count()
            log_kwargs["sql_queries"] = sql_queries
            if sql_queries > HIGH_SQL_QUERY_THRESHOLD:
                structlog.get_logger().warning("high_sql_query_count", **log_kwargs)
        structlog.get_logger().info("request_completed", **log_kwargs)
        return response
