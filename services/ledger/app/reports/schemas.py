from pydantic import BaseModel, Field


class MonthSummary(BaseModel):
    month: int = Field(ge=1, le=12)
    total: str
    count: int


class MonthlyReportRead(BaseModel):
    year: int | None
    months: list[MonthSummary]
    grand_total: str
