from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.categories.service import get_owned_category
from app.core.exceptions import NotFoundError
from app.expenses.models import Expense
from app.expenses.schemas import ExpenseCreate, ExpenseRead, ExpenseUpdate
from app.tags.models import Tag


def _expense_load_options():
    return (
        joinedload(Expense.category),
        selectinload(Expense.tags),
    )


async def list_expenses(session: AsyncSession, user_id: UUID) -> list[ExpenseRead]:
    result = await session.scalars(
        select(Expense)
        .where(Expense.user_id == user_id)
        .options(*_expense_load_options())
        .order_by(Expense.expense_date.desc(), Expense.created_at.desc())
    )
    return [ExpenseRead.model_validate(row) for row in result.unique().all()]


async def create_expense(session: AsyncSession, user_id: UUID, data: ExpenseCreate) -> ExpenseRead:
    category = await get_owned_category(session, user_id, data.category_id)
    tags = await _get_owned_tags(session, user_id, data.tag_ids)
    expense = Expense(
        user_id=user_id,
        category_id=category.id,
        amount=Decimal(data.amount),
        description=data.description,
        expense_date=data.expense_date,
        tags=tags,
    )
    session.add(expense)
    await session.commit()
    return await get_expense(session, user_id, expense.id)


async def get_expense(session: AsyncSession, user_id: UUID, expense_id: UUID) -> ExpenseRead:
    expense = await _get_owned_expense(session, user_id, expense_id)
    return ExpenseRead.model_validate(expense)


async def update_expense(
    session: AsyncSession, user_id: UUID, expense_id: UUID, data: ExpenseUpdate
) -> ExpenseRead:
    expense = await _get_owned_expense(session, user_id, expense_id)
    category = await get_owned_category(session, user_id, data.category_id)
    tags = await _get_owned_tags(session, user_id, data.tag_ids)
    expense.category_id = category.id
    expense.amount = Decimal(data.amount)
    expense.description = data.description
    expense.expense_date = data.expense_date
    expense.updated_at = datetime.now(UTC)
    expense.tags = tags
    await session.commit()
    return await get_expense(session, user_id, expense_id)


async def delete_expense(session: AsyncSession, user_id: UUID, expense_id: UUID) -> None:
    expense = await _get_owned_expense(session, user_id, expense_id)
    await session.delete(expense)
    await session.commit()


async def _get_owned_expense(session: AsyncSession, user_id: UUID, expense_id: UUID) -> Expense:
    expense = await session.scalar(
        select(Expense)
        .where(Expense.id == expense_id, Expense.user_id == user_id)
        .options(*_expense_load_options())
    )
    if expense is None:
        raise NotFoundError("expense")
    return expense


async def _get_owned_tags(session: AsyncSession, user_id: UUID, tag_ids: list[UUID]) -> list[Tag]:
    if not tag_ids:
        return []
    result = await session.scalars(select(Tag).where(Tag.user_id == user_id, Tag.id.in_(tag_ids)))
    tags = list(result.all())
    if len(tags) != len(set(tag_ids)):
        raise NotFoundError("tag")
    return tags
