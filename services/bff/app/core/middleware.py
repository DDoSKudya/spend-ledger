from collections.abc import Awaitable, Callable

import jwt
from fastapi import FastAPI, Request
from starlette.responses import Response

from app.core.config import settings
from app.core.exceptions import InvalidTokenError, MissingBearerTokenError
from spend_ledger_common.constants import ACCESS_TOKEN_TYPE
from spend_ledger_common.error_handlers import error_response_for

PROTECTED_PREFIXES = (
    "/api/v1/categories",
    "/api/v1/tags",
    "/api/v1/expenses",
    "/api/v1/reports",
    "/api/v1/exports",
)


def register_auth_middleware(app: FastAPI) -> None:
    @app.middleware("http")
    async def auth_middleware(
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
