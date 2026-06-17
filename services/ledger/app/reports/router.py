from uuid import UUID

from fastapi import APIRouter, Query

from app.core.deps import CurrentUserId
from app.reports import service
from app.reports.schemas import MonthlyReportRead

router = APIRouter(prefix="/internal/v1/reports", tags=["reports"])


@router.get("/monthly", response_model=MonthlyReportRead)
async def monthly_report(
    user_id: CurrentUserId,
    year: int | None = Query(default=None, ge=2000, le=2100),
    category_id: UUID | None = None,
) -> MonthlyReportRead:
    return await service.monthly_report(user_id, year=year, category_id=category_id)
