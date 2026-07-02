from contextvars import ContextVar
from typing import Annotated
from uuid import UUID

from fastapi import Depends

from app.core.exceptions import MissingUserIdError
from spend_ledger_common.deps import make_get_user_id

sql_query_count: ContextVar[int] = ContextVar("sql_query_count", default=0)


def reset_sql_count() -> None:
    sql_query_count.set(0)


def increment_sql_count() -> None:
    sql_query_count.set(sql_query_count.get() + 1)


def get_sql_count() -> int:
    return sql_query_count.get()


get_user_id = make_get_user_id(MissingUserIdError)
CurrentUserId = Annotated[UUID, Depends(get_user_id)]
