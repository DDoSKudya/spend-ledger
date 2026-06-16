from collections.abc import AsyncIterator
from contextvars import ContextVar
from typing import Annotated
from uuid import UUID

from fastapi import Depends, Header, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings

sql_query_count: ContextVar[int] = ContextVar("sql_query_count", default=0)

OptionalUserIdHeader = Annotated[UUID | None, Header(alias="X-User-Id")]


def reset_sql_count() -> None:
    sql_query_count.set(0)


def increment_sql_count() -> None:
    sql_query_count.set(sql_query_count.get() + 1)


def get_sql_count() -> int:
    return sql_query_count.get()


async def get_db(request: Request) -> AsyncIterator[AsyncSession]:
    session_factory = request.app.state.session_factory
    async with session_factory() as session:
        yield session


def get_user_id(x_user_id: OptionalUserIdHeader) -> UUID:
    if x_user_id is not None:
        return x_user_id
    if settings.APP_ENV == "development":
        return settings.DEV_USER_ID
    raise HTTPException(status_code=401, detail="Missing X-User-Id header")


DbSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUserId = Annotated[UUID, Depends(get_user_id)]
