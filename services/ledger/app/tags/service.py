from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.core.exceptions import DuplicateNameError, NotFoundError
from app.tags.models import Tag
from app.tags.schemas import TagCreate, TagRead, TagUpdate
from spend_ledger_common.session import get_session


async def list_tags(user_id: UUID) -> list[TagRead]:
    session = get_session()
    result = await session.scalars(select(Tag).where(Tag.user_id == user_id).order_by(Tag.name))
    return [TagRead.model_validate(row) for row in result.all()]


async def create_tag(user_id: UUID, data: TagCreate) -> TagRead:
    session = get_session()
    tag = Tag(user_id=user_id, name=data.name.strip())
    session.add(tag)
    try:
        await session.flush()
    except IntegrityError as exc:
        raise DuplicateNameError("tag") from exc
    return TagRead.model_validate(tag)


async def get_tag(user_id: UUID, tag_id: UUID) -> TagRead:
    tag = await _get_owned_tag(user_id, tag_id)
    return TagRead.model_validate(tag)


async def update_tag(user_id: UUID, tag_id: UUID, data: TagUpdate) -> TagRead:
    session = get_session()
    tag = await _get_owned_tag(user_id, tag_id)
    tag.name = data.name.strip()
    try:
        await session.flush()
    except IntegrityError as exc:
        raise DuplicateNameError("tag") from exc
    return TagRead.model_validate(tag)


async def delete_tag(user_id: UUID, tag_id: UUID) -> None:
    session = get_session()
    tag = await _get_owned_tag(user_id, tag_id)
    await session.delete(tag)


async def _get_owned_tag(user_id: UUID, tag_id: UUID) -> Tag:
    session = get_session()
    tag = await session.scalar(select(Tag).where(Tag.id == tag_id, Tag.user_id == user_id))
    if tag is None:
        raise NotFoundError("tag")
    return tag
