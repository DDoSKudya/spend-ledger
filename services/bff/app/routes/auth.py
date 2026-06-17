import json

from fastapi import APIRouter, Request, Response
from fastapi.responses import JSONResponse

from app.clients.proxy import forward_to_auth
from app.core.config import settings
from app.core.constants import HTTP_OK
from app.core.exceptions import (
    InvalidUpstreamResponseError,
    MissingBearerTokenError,
    MissingRefreshTokenError,
)

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


def _set_refresh_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=settings.REFRESH_COOKIE_NAME,
        value=token,
        httponly=True,
        secure=settings.APP_ENV != "development",
        samesite="lax",
        max_age=settings.JWT_REFRESH_EXPIRE_DAYS * 24 * 60 * 60,
        path="/api/v1/auth",
    )


def _extract_session_payload(response: Response) -> tuple[dict, str]:
    try:
        parsed = json.loads(bytes(response.body).decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise InvalidUpstreamResponseError() from exc
    refresh_token = parsed.pop("refresh_token", None)
    if not isinstance(refresh_token, str) or not refresh_token:
        raise InvalidUpstreamResponseError()
    return parsed, refresh_token


@router.post("/register")
async def register(request: Request) -> Response:
    payload = await request.json()
    return await forward_to_auth(request, "/internal/v1/auth/register", payload)


@router.post("/login")
async def login(request: Request) -> Response:
    payload = await request.json()
    auth_response = await forward_to_auth(request, "/internal/v1/auth/login", payload)
    if auth_response.status_code != HTTP_OK:
        return auth_response

    parsed, refresh_token = _extract_session_payload(auth_response)
    response = JSONResponse(status_code=HTTP_OK, content=parsed)
    _set_refresh_cookie(response, refresh_token)
    return response


@router.post("/refresh")
async def refresh(request: Request) -> Response:
    refresh_token = request.cookies.get(settings.REFRESH_COOKIE_NAME)
    if not refresh_token:
        raise MissingRefreshTokenError()

    auth_response = await forward_to_auth(
        request,
        "/internal/v1/auth/refresh",
        {"refresh_token": refresh_token},
    )
    if auth_response.status_code != HTTP_OK:
        return auth_response

    parsed, new_refresh = _extract_session_payload(auth_response)
    response = JSONResponse(status_code=HTTP_OK, content=parsed)
    _set_refresh_cookie(response, new_refresh)
    return response


@router.post("/logout", status_code=204)
async def logout(request: Request) -> Response:
    refresh_token = request.cookies.get(settings.REFRESH_COOKIE_NAME)
    if refresh_token:
        await forward_to_auth(request, "/internal/v1/auth/logout", {"refresh_token": refresh_token})

    response = Response(status_code=204)
    response.delete_cookie(settings.REFRESH_COOKIE_NAME, path="/api/v1/auth")
    return response


@router.get("/me")
async def me(request: Request) -> Response:
    if not request.headers.get("Authorization"):
        raise MissingBearerTokenError()
    return await forward_to_auth(request, "/internal/v1/auth/verify")
