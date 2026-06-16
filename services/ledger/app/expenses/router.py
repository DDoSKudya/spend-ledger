from uuid import UUID

from fastapi import APIRouter, status

from app.core.deps import CurrentUserId, DbSession
from app.expenses import service
from app.expenses.schemas import ExpenseCreate, ExpenseRead, ExpenseUpdate

router = APIRouter(prefix="/internal/v1/expenses", tags=["expenses"])


@router.get("", response_model=list[ExpenseRead])
async def list_expenses(
    session: DbSession,
    user_id: CurrentUserId,
) -> list[ExpenseRead]:
    return await service.list_expenses(session, user_id)


@router.post("", response_model=ExpenseRead, status_code=status.HTTP_201_CREATED)
async def create_expense(
    data: ExpenseCreate,
    session: DbSession,
    user_id: CurrentUserId,
) -> ExpenseRead:
    return await service.create_expense(session, user_id, data)


@router.get("/{expense_id}", response_model=ExpenseRead)
async def get_expense(
    expense_id: UUID,
    session: DbSession,
    user_id: CurrentUserId,
) -> ExpenseRead:
    return await service.get_expense(session, user_id, expense_id)


@router.put("/{expense_id}", response_model=ExpenseRead)
async def update_expense(
    expense_id: UUID,
    data: ExpenseUpdate,
    session: DbSession,
    user_id: CurrentUserId,
) -> ExpenseRead:
    return await service.update_expense(session, user_id, expense_id, data)


@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_expense(
    expense_id: UUID,
    session: DbSession,
    user_id: CurrentUserId,
) -> None:
    await service.delete_expense(session, user_id, expense_id)
