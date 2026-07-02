from dataclasses import dataclass
from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import exists, func, select
from sqlalchemy.orm import joinedload, selectinload

from app.categories.service import get_owned_category
from app.core.exceptions import NotFoundError, ValidationError
from app.core.pagination import build_page
from app.expenses.models import Expense, ExpenseTag
from app.expenses.schemas import ExpenseCreate, ExpensePage, ExpenseRead, ExpenseUpdate
from app.tags.models import Tag
from spend_ledger_common.session import get_session

SORT_COLUMNS = {
    "expense_date": Expense.expense_date,
    "amount": Expense.amount,
    "created_at": Expense.created_at,
}


@dataclass(frozen=True)
class ExpenseListFilters:
    page: int
    size: int
    sort_field: str
    sort_desc: bool
    category_id: UUID | None
    tag_ids: list[UUID]
    date_from: date | None
    date_to: date | None
    search: str | None


def parse_sort(sort: str) -> tuple[str, bool]:
    parts = sort.split(":", 1)
    if len(parts) != 2:
        raise ValidationError("sort must be field:direction")
    field, direction = parts
    if field not in SORT_COLUMNS:
        raise ValidationError(f"Invalid sort field: {field}")
    if direction not in {"asc", "desc"}:
        raise ValidationError(f"Invalid sort direction: {direction}")
    return field, direction == "desc"


def _expense_load_options():
    return (
        joinedload(Expense.category),
        selectinload(Expense.tags),
    )


def _expense_select():
    return select(Expense).options(*_expense_load_options())


def _apply_filters(stmt, user_id: UUID, filters: ExpenseListFilters):
    stmt = stmt.where(Expense.user_id == user_id)
    if filters.category_id is not None:
        stmt = stmt.where(Expense.category_id == filters.category_id)
    if filters.date_from is not None:
        stmt = stmt.where(Expense.expense_date >= filters.date_from)
    if filters.date_to is not None:
        stmt = stmt.where(Expense.expense_date <= filters.date_to)
    if filters.search:
        stmt = stmt.where(Expense.description.ilike(f"%{filters.search}%"))
    if filters.tag_ids:
        stmt = stmt.where(
            exists(
                select(1)
                .select_from(ExpenseTag)
                .where(
                    ExpenseTag.expense_id == Expense.id,
                    ExpenseTag.tag_id.in_(filters.tag_ids),
                )
            )
        )
    return stmt


async def list_expenses(user_id: UUID, filters: ExpenseListFilters) -> ExpensePage:
    session = get_session()
    count_stmt = _apply_filters(select(func.count()).select_from(Expense), user_id, filters)
    total = await session.scalar(count_stmt) or 0

    sort_column = SORT_COLUMNS[filters.sort_field]
    order = sort_column.desc() if filters.sort_desc else sort_column.asc()
    offset = (filters.page - 1) * filters.size

    list_stmt = (
        _apply_filters(_expense_select(), user_id, filters)
        .order_by(order, Expense.created_at.desc())
        .offset(offset)
        .limit(filters.size)
    )
    result = await session.scalars(list_stmt)
    items = [ExpenseRead.model_validate(row) for row in result.unique().all()]
    return build_page(items, total=total, page=filters.page, size=filters.size)


async def create_expense(user_id: UUID, data: ExpenseCreate) -> ExpenseRead:
    session = get_session()
    category = await get_owned_category(user_id, data.category_id)
    tags = await _get_owned_tags(user_id, data.tag_ids)
    expense = Expense(
        user_id=user_id,
        category_id=category.id,
        category=category,
        amount=Decimal(data.amount),
        description=data.description,
        expense_date=data.expense_date,
        tags=tags,
    )
    session.add(expense)
    await session.flush()
    return ExpenseRead.model_validate(expense)


async def get_expense(user_id: UUID, expense_id: UUID) -> ExpenseRead:
    expense = await _get_owned_expense(user_id, expense_id)
    return ExpenseRead.model_validate(expense)


async def update_expense(user_id: UUID, expense_id: UUID, data: ExpenseUpdate) -> ExpenseRead:
    session = get_session()
    expense = await _get_owned_expense(user_id, expense_id)
    category = await get_owned_category(user_id, data.category_id)
    tags = await _get_owned_tags(user_id, data.tag_ids)
    expense.category_id = category.id
    expense.category = category
    expense.amount = Decimal(data.amount)
    expense.description = data.description
    expense.expense_date = data.expense_date
    expense.updated_at = datetime.now(UTC)
    expense.tags = tags
    await session.flush()
    return ExpenseRead.model_validate(expense)


async def delete_expense(user_id: UUID, expense_id: UUID) -> None:
    session = get_session()
    expense = await _get_owned_expense(user_id, expense_id)
    await session.delete(expense)


async def _get_owned_expense(user_id: UUID, expense_id: UUID) -> Expense:
    session = get_session()
    expense = await session.scalar(
        _expense_select().where(Expense.id == expense_id, Expense.user_id == user_id)
    )
    if expense is None:
        raise NotFoundError("expense")
    return expense


async def _get_owned_tags(user_id: UUID, tag_ids: list[UUID]) -> list[Tag]:
    if not tag_ids:
        return []
    session = get_session()
    result = await session.scalars(select(Tag).where(Tag.user_id == user_id, Tag.id.in_(tag_ids)))
    tags = list(result.all())
    if len(tags) != len(set(tag_ids)):
        raise NotFoundError("tag")
    return tags
