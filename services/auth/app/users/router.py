from fastapi import APIRouter, Header, HTTPException

from app.core.deps import DbSession
from app.users import service
from app.users.schemas import (
    AuthSessionResponse,
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    RegisterRequest,
    UserRead,
)

router = APIRouter(prefix="/internal/v1/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=201)
async def register(data: RegisterRequest, session: DbSession) -> UserRead:
    return await service.register_user(session, data)


@router.post("/login", response_model=AuthSessionResponse)
async def login(data: LoginRequest, session: DbSession) -> AuthSessionResponse:
    token_response, refresh_token = await service.login_user(session, data)
    return AuthSessionResponse(**token_response.model_dump(), refresh_token=refresh_token)


@router.post("/refresh", response_model=AuthSessionResponse)
async def refresh(data: RefreshRequest, session: DbSession) -> AuthSessionResponse:
    token_response, refresh_token = await service.refresh_access_token(session, data.refresh_token)
    return AuthSessionResponse(**token_response.model_dump(), refresh_token=refresh_token)


@router.post("/logout", status_code=204)
async def logout(data: LogoutRequest, session: DbSession) -> None:
    await service.revoke_refresh_token(session, data.refresh_token)


@router.get("/verify", response_model=UserRead)
async def verify(
    session: DbSession,
    authorization: str | None = Header(default=None, alias="Authorization"),
) -> UserRead:
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")
    token = authorization.split(" ", maxsplit=1)[1]
    return await service.verify_access_token(session, token)
