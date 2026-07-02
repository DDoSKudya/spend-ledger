from collections.abc import Callable
from typing import Annotated
from uuid import UUID

from fastapi import Header

OptionalUserIdHeader = Annotated[UUID | None, Header(alias="X-User-Id")]


def make_get_user_id[E: Exception](error_type: Callable[[], E]) -> Callable[..., UUID]:
    def get_user_id(x_user_id: OptionalUserIdHeader = None) -> UUID:
        if x_user_id is None:
            raise error_type()
        return x_user_id

    return get_user_id
