from typing import Annotated
from uuid import UUID

from fastapi import Depends, Header, HTTPException

OptionalUserIdHeader = Annotated[UUID | None, Header(alias="X-User-Id")]


def get_user_id(x_user_id: OptionalUserIdHeader = None) -> UUID:
    if x_user_id is None:
        raise HTTPException(status_code=401, detail="Missing X-User-Id header")
    return x_user_id


CurrentUserId = Annotated[UUID, Depends(get_user_id)]
