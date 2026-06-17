from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.categories.schemas import CategoryRead
from app.core.pagination import Page
from app.core.schemas import AmountMixin
from app.tags.schemas import TagRead


class ExpenseWrite(BaseModel):
    amount: Decimal = Field(gt=0)
    category_id: UUID
    tag_ids: list[UUID] = Field(default_factory=list)
    description: str | None = None
    expense_date: date


ExpenseCreate = ExpenseWrite
ExpenseUpdate = ExpenseWrite


class ExpenseRead(AmountMixin):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    description: str | None
    expense_date: date
    created_at: datetime
    updated_at: datetime
    category: CategoryRead
    tags: list[TagRead]


ExpensePage = Page[ExpenseRead]
