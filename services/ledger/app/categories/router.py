from uuid import UUID

from fastapi import APIRouter, status

from app.categories import service
from app.categories.schemas import CategoryCreate, CategoryRead, CategoryUpdate
from app.core.deps import CurrentUserId, DbSession

router = APIRouter(prefix="/internal/v1/categories", tags=["categories"])


@router.get("", response_model=list[CategoryRead])
async def list_categories(
    session: DbSession,
    user_id: CurrentUserId,
) -> list[CategoryRead]:
    return await service.list_categories(session, user_id)


@router.post("", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
async def create_category(
    data: CategoryCreate,
    session: DbSession,
    user_id: CurrentUserId,
) -> CategoryRead:
    return await service.create_category(session, user_id, data)


@router.get("/{category_id}", response_model=CategoryRead)
async def get_category(
    category_id: UUID,
    session: DbSession,
    user_id: CurrentUserId,
) -> CategoryRead:
    return await service.get_category(session, user_id, category_id)


@router.put("/{category_id}", response_model=CategoryRead)
async def update_category(
    category_id: UUID,
    data: CategoryUpdate,
    session: DbSession,
    user_id: CurrentUserId,
) -> CategoryRead:
    return await service.update_category(session, user_id, category_id, data)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: UUID,
    session: DbSession,
    user_id: CurrentUserId,
) -> None:
    await service.delete_category(session, user_id, category_id)
