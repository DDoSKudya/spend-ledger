from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from app.categories.models import Category
from app.categories.schemas import CategoryCreate, CategoryRead, CategoryUpdate
from app.core.exceptions import CategoryInUseError, DuplicateNameError, NotFoundError
from app.expenses.models import Expense
from spend_ledger_common.session import get_session


async def list_categories(user_id: UUID) -> list[CategoryRead]:
    session = get_session()
    result = await session.scalars(
        select(Category).where(Category.user_id == user_id).order_by(Category.name)
    )
    return [CategoryRead.model_validate(row) for row in result.all()]


async def create_category(user_id: UUID, data: CategoryCreate) -> CategoryRead:
    session = get_session()
    category = Category(user_id=user_id, name=data.name.strip())
    session.add(category)
    try:
        await session.flush()
    except IntegrityError as exc:
        raise DuplicateNameError("category") from exc
    return CategoryRead.model_validate(category)


async def get_category(user_id: UUID, category_id: UUID) -> CategoryRead:
    category = await get_owned_category(user_id, category_id)
    return CategoryRead.model_validate(category)


async def update_category(user_id: UUID, category_id: UUID, data: CategoryUpdate) -> CategoryRead:
    session = get_session()
    category = await get_owned_category(user_id, category_id)
    category.name = data.name.strip()
    try:
        await session.flush()
    except IntegrityError as exc:
        raise DuplicateNameError("category") from exc
    return CategoryRead.model_validate(category)


async def delete_category(user_id: UUID, category_id: UUID) -> None:
    session = get_session()
    category = await get_owned_category(user_id, category_id)
    expense_count = await session.scalar(
        select(func.count())
        .select_from(Expense)
        .where(Expense.user_id == user_id, Expense.category_id == category_id)
    )
    if expense_count:
        raise CategoryInUseError(expense_count)
    await session.delete(category)


async def get_owned_category(user_id: UUID, category_id: UUID) -> Category:
    session = get_session()
    category = await session.scalar(
        select(Category).where(Category.id == category_id, Category.user_id == user_id)
    )
    if category is None:
        raise NotFoundError("category")
    return category
