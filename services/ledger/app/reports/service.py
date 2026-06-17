from decimal import Decimal
from uuid import UUID

from sqlalchemy import extract, func, select

from app.core.schemas import serialize_amount
from app.core.session import get_session
from app.expenses.models import Expense
from app.reports.schemas import MonthlyReportRead, MonthSummary


async def monthly_report(
    user_id: UUID,
    *,
    year: int | None,
    category_id: UUID | None,
) -> MonthlyReportRead:
    session = get_session()
    month_start = func.date_trunc("month", Expense.expense_date).label("month_start")
    stmt = (
        select(
            month_start,
            func.sum(Expense.amount).label("total"),
            func.count(Expense.id).label("expense_count"),
        )
        .where(Expense.user_id == user_id)
        .group_by(month_start)
        .order_by(month_start)
    )
    if year is not None:
        stmt = stmt.where(extract("year", Expense.expense_date) == year)
    if category_id is not None:
        stmt = stmt.where(Expense.category_id == category_id)

    rows = (await session.execute(stmt)).all()
    months: list[MonthSummary] = []
    grand_total = Decimal("0")
    for row in rows:
        total = row.total or Decimal("0")
        grand_total += total
        months.append(
            MonthSummary(
                month=row.month_start.month,
                total=serialize_amount(total),
                count=row.expense_count,
            )
        )

    return MonthlyReportRead(
        year=year,
        months=months,
        grand_total=serialize_amount(grand_total),
    )
