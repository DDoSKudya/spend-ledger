from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.categories.models import Category
from app.categories.schemas import CategoryCreate, CategoryRead, CategoryUpdate
from app.core.exceptions import CategoryInUseError, DuplicateNameError, NotFoundError
from app.expenses.models import Expense


async def list_categories(session: AsyncSession, user_id: UUID) -> list[CategoryRead]:
    result = await session.scalars(
        select(Category).where(Category.user_id == user_id).order_by(Category.name)
    )
    return [CategoryRead.model_validate(row) for row in result.all()]


async def create_category(
    session: AsyncSession, user_id: UUID, data: CategoryCreate
) -> CategoryRead:
    category = Category(user_id=user_id, name=data.name.strip())
    session.add(category)
    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise DuplicateNameError("category") from exc
    await session.refresh(category)
    return CategoryRead.model_validate(category)


async def get_category(session: AsyncSession, user_id: UUID, category_id: UUID) -> CategoryRead:
    category = await get_owned_category(session, user_id, category_id)
    return CategoryRead.model_validate(category)


async def update_category(
    session: AsyncSession, user_id: UUID, category_id: UUID, data: CategoryUpdate
) -> CategoryRead:
    category = await get_owned_category(session, user_id, category_id)
    category.name = data.name.strip()
    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise DuplicateNameError("category") from exc
    await session.refresh(category)
    return CategoryRead.model_validate(category)


async def delete_category(session: AsyncSession, user_id: UUID, category_id: UUID) -> None:
    category = await get_owned_category(session, user_id, category_id)
    expense_count = await session.scalar(
        select(func.count())
        .select_from(Expense)
        .where(Expense.user_id == user_id, Expense.category_id == category_id)
    )
    if expense_count:
        raise CategoryInUseError(expense_count)
    await session.delete(category)
    await session.commit()


async def get_owned_category(session: AsyncSession, user_id: UUID, category_id: UUID) -> Category:
    category = await session.scalar(
        select(Category).where(Category.id == category_id, Category.user_id == user_id)
    )
    if category is None:
        raise NotFoundError("category")
    return category
