from typing import Annotated
from uuid import UUID

from fastapi import Depends

from app.core.exceptions import MissingUserIdError
from spend_ledger_common.deps import make_get_user_id

get_user_id = make_get_user_id(MissingUserIdError)
CurrentUserId = Annotated[UUID, Depends(get_user_id)]
