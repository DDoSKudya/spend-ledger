from datetime import date
from uuid import UUID

from fastapi import APIRouter, Query, status

from app.core.deps import CurrentUserId
from app.expenses import service
from app.expenses.schemas import ExpenseCreate, ExpensePage, ExpenseRead, ExpenseUpdate
from app.expenses.service import ExpenseListFilters, parse_sort

router = APIRouter(prefix="/internal/v1/expenses", tags=["expenses"])


@router.get("", response_model=ExpensePage)
async def list_expenses(
    user_id: CurrentUserId,
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    sort: str = Query(default="expense_date:desc"),
    category_id: UUID | None = None,
    tag_ids: list[UUID] = Query(default=[]),
    date_from: date | None = None,
    date_to: date | None = None,
    search: str | None = None,
) -> ExpensePage:
    sort_field, sort_desc = parse_sort(sort)
    filters = ExpenseListFilters(
        page=page,
        size=size,
        sort_field=sort_field,
        sort_desc=sort_desc,
        category_id=category_id,
        tag_ids=tag_ids,
        date_from=date_from,
        date_to=date_to,
        search=search,
    )
    return await service.list_expenses(user_id, filters)


@router.post("", response_model=ExpenseRead, status_code=status.HTTP_201_CREATED)
async def create_expense(data: ExpenseCreate, user_id: CurrentUserId) -> ExpenseRead:
    return await service.create_expense(user_id, data)


@router.get("/{expense_id}", response_model=ExpenseRead)
async def get_expense(expense_id: UUID, user_id: CurrentUserId) -> ExpenseRead:
    return await service.get_expense(user_id, expense_id)


@router.put("/{expense_id}", response_model=ExpenseRead)
async def update_expense(
    expense_id: UUID,
    data: ExpenseUpdate,
    user_id: CurrentUserId,
) -> ExpenseRead:
    return await service.update_expense(user_id, expense_id, data)


@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_expense(expense_id: UUID, user_id: CurrentUserId) -> None:
    await service.delete_expense(user_id, expense_id)
