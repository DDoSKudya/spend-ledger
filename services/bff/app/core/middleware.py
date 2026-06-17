import time
from collections.abc import Awaitable, Callable
from uuid import uuid4

import jwt
import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.config import settings
from app.core.error_handlers import error_response_for
from app.core.exceptions import InvalidTokenError, MissingBearerTokenError

SERVICE_NAME = "bff"
ACCESS_TOKEN_TYPE = "access"  # noqa: S105
PROTECTED_PREFIXES = (
    "/api/v1/categories",
    "/api/v1/tags",
    "/api/v1/expenses",
    "/api/v1/reports",
    "/api/v1/exports",
)


class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        request_id = request.headers.get("X-Request-Id")
        if request_id is None:
            request_id = str(uuid4())

        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id, service=SERVICE_NAME)
        response = await call_next(request)
        response.headers["X-Request-Id"] = request_id
        return response


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        if not request.url.path.startswith(PROTECTED_PREFIXES):
            return await call_next(request)

        authorization = request.headers.get("Authorization")
        if authorization is None or not authorization.startswith("Bearer "):
            return error_response_for(MissingBearerTokenError())

        token = authorization.split(" ", maxsplit=1)[1]
        try:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        except jwt.PyJWTError:
            return error_response_for(InvalidTokenError())

        user_id = payload.get("sub")
        token_type = payload.get("type")
        if token_type != ACCESS_TOKEN_TYPE or not user_id:
            return error_response_for(InvalidTokenError())

        request.state.user_id = user_id
        return await call_next(request)


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
