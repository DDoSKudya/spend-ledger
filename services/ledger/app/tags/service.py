from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import DuplicateNameError, NotFoundError
from app.tags.models import Tag
from app.tags.schemas import TagCreate, TagRead, TagUpdate


async def list_tags(session: AsyncSession, user_id: UUID) -> list[TagRead]:
    result = await session.scalars(select(Tag).where(Tag.user_id == user_id).order_by(Tag.name))
    return [TagRead.model_validate(row) for row in result.all()]


async def create_tag(session: AsyncSession, user_id: UUID, data: TagCreate) -> TagRead:
    tag = Tag(user_id=user_id, name=data.name.strip())
    session.add(tag)
    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise DuplicateNameError("tag") from exc
    await session.refresh(tag)
    return TagRead.model_validate(tag)


async def get_tag(session: AsyncSession, user_id: UUID, tag_id: UUID) -> TagRead:
    tag = await _get_owned_tag(session, user_id, tag_id)
    return TagRead.model_validate(tag)


async def update_tag(
    session: AsyncSession, user_id: UUID, tag_id: UUID, data: TagUpdate
) -> TagRead:
    tag = await _get_owned_tag(session, user_id, tag_id)
    tag.name = data.name.strip()
    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise DuplicateNameError("tag") from exc
    await session.refresh(tag)
    return TagRead.model_validate(tag)


async def delete_tag(session: AsyncSession, user_id: UUID, tag_id: UUID) -> None:
    tag = await _get_owned_tag(session, user_id, tag_id)
    await session.delete(tag)
    await session.commit()


async def _get_owned_tag(session: AsyncSession, user_id: UUID, tag_id: UUID) -> Tag:
    tag = await session.scalar(select(Tag).where(Tag.id == tag_id, Tag.user_id == user_id))
    if tag is None:
        raise NotFoundError("tag")
    return tag
