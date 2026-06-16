from uuid import UUID

from fastapi import APIRouter, status

from app.core.deps import CurrentUserId, DbSession
from app.tags import service
from app.tags.schemas import TagCreate, TagRead, TagUpdate

router = APIRouter(prefix="/internal/v1/tags", tags=["tags"])


@router.get("", response_model=list[TagRead])
async def list_tags(
    session: DbSession,
    user_id: CurrentUserId,
) -> list[TagRead]:
    return await service.list_tags(session, user_id)


@router.post("", response_model=TagRead, status_code=status.HTTP_201_CREATED)
async def create_tag(
    data: TagCreate,
    session: DbSession,
    user_id: CurrentUserId,
) -> TagRead:
    return await service.create_tag(session, user_id, data)


@router.get("/{tag_id}", response_model=TagRead)
async def get_tag(
    tag_id: UUID,
    session: DbSession,
    user_id: CurrentUserId,
) -> TagRead:
    return await service.get_tag(session, user_id, tag_id)


@router.patch("/{tag_id}", response_model=TagRead)
async def update_tag(
    tag_id: UUID,
    data: TagUpdate,
    session: DbSession,
    user_id: CurrentUserId,
) -> TagRead:
    return await service.update_tag(session, user_id, tag_id, data)


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(
    tag_id: UUID,
    session: DbSession,
    user_id: CurrentUserId,
) -> None:
    await service.delete_tag(session, user_id, tag_id)
