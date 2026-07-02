from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.core.config import settings
from app.core.exceptions import (
    DuplicateEmailError,
    InvalidCredentialsError,
    InvalidTokenError,
    UserNotFoundError,
)
from app.core.security import (
    ACCESS_TOKEN_TYPE,
    REFRESH_TOKEN_TYPE,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    hash_refresh_token,
    verify_password,
)
from app.users.models import RefreshToken, User
from app.users.schemas import LoginRequest, RegisterRequest, TokenResponse, UserRead
from spend_ledger_common.session import get_session


async def register_user(data: RegisterRequest) -> UserRead:
    session = get_session()
    user = User(email=data.email.lower(), password_hash=hash_password(data.password))
    session.add(user)
    try:
        await session.flush()
    except IntegrityError as exc:
        raise DuplicateEmailError() from exc
    return UserRead.model_validate(user)


async def login_user(data: LoginRequest) -> tuple[TokenResponse, str]:
    session = get_session()
    user = await session.scalar(select(User).where(User.email == data.email.lower()))
    if user is None or not verify_password(data.password, user.password_hash):
        raise InvalidCredentialsError()
    return await _issue_tokens(user.id)


async def refresh_access_token(refresh_token: str) -> tuple[TokenResponse, str]:
    session = get_session()
    payload = decode_token(refresh_token, REFRESH_TOKEN_TYPE)
    token_hash = hash_refresh_token(refresh_token)
    token_row = await session.scalar(
        select(RefreshToken).where(RefreshToken.token_hash == token_hash)
    )
    if token_row is None or token_row.revoked_at is not None:
        raise InvalidTokenError("invalid_refresh_token")
    if token_row.expires_at <= datetime.now(UTC):
        raise InvalidTokenError("expired_refresh_token")

    token_row.revoked_at = datetime.now(UTC)
    user_id = UUID(payload["sub"])
    user = await session.get(User, user_id)
    if user is None:
        raise UserNotFoundError()
    return await _issue_tokens(user_id)


async def revoke_refresh_token(refresh_token: str) -> None:
    session = get_session()
    token_hash = hash_refresh_token(refresh_token)
    token_row = await session.scalar(
        select(RefreshToken).where(RefreshToken.token_hash == token_hash)
    )
    if token_row is not None and token_row.revoked_at is None:
        token_row.revoked_at = datetime.now(UTC)


async def verify_access_token(token: str) -> UserRead:
    session = get_session()
    payload = decode_token(token, ACCESS_TOKEN_TYPE)
    user_id = UUID(payload["sub"])
    user = await session.get(User, user_id)
    if user is None:
        raise UserNotFoundError()
    return UserRead.model_validate(user)


async def _issue_tokens(user_id: UUID) -> tuple[TokenResponse, str]:
    session = get_session()
    access_token = create_access_token(user_id)
    refresh_token = create_refresh_token(user_id)
    session.add(
        RefreshToken(
            user_id=user_id,
            token_hash=hash_refresh_token(refresh_token),
            expires_at=_refresh_expires_at(),
        )
    )
    await session.flush()
    return (
        TokenResponse(
            access_token=access_token,
            expires_in=settings.JWT_ACCESS_EXPIRE_MINUTES * 60,
        ),
        refresh_token,
    )


def _refresh_expires_at() -> datetime:
    return datetime.now(UTC).replace(microsecond=0) + timedelta(
        days=settings.JWT_REFRESH_EXPIRE_DAYS
    )
