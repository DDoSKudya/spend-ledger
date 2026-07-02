import time
from collections.abc import Awaitable, Callable

import structlog
from fastapi import FastAPI, Request
from starlette.responses import Response

from app.core.config import settings
from app.core.deps import get_sql_count, reset_sql_count

HIGH_SQL_QUERY_THRESHOLD = 10


def register_sql_profile_middleware(app: FastAPI) -> None:
    @app.middleware("http")
    async def sql_profile_middleware(
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


def register_pyinstrument_middleware(app: FastAPI) -> None:
    @app.middleware("http")
    async def pyinstrument_middleware(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        if not settings.ENABLE_PYINSTRUMENT:
            return await call_next(request)

        import pyinstrument

        profiler = pyinstrument.Profiler(async_mode="enabled")
        profiler.start()
        try:
            return await call_next(request)
        finally:
            profiler.stop()
            structlog.get_logger().info(
                "pyinstrument_profile",
                path=request.url.path,
                profile=profiler.output_text(unicode=False, color=False),
            )
