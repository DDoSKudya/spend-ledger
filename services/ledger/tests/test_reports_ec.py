import os

import pytest

pytestmark = pytest.mark.skipif(
    os.getenv("LEDGER_INTEGRATION", "").lower() not in {"1", "true", "yes"},
    reason="Set LEDGER_INTEGRATION=1 and LEDGER_DATABASE_URL for integration tests",
)


@pytest.mark.asyncio
async def test_monthly_report_aggregates_by_month(integration_client, expense_dataset) -> None:
    """EC-P0 valid: monthly totals and counts are aggregated."""
    response = await integration_client.get(
        "/internal/v1/reports/monthly",
        params={"year": 2026},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["year"] == 2026
    assert body["grand_total"] == "65.50"
    assert body["months"] == [
        {"month": 6, "total": "57.50", "count": 2},
        {"month": 7, "total": "8.00", "count": 1},
    ]


@pytest.mark.asyncio
async def test_monthly_report_category_filter_limits_totals(
    integration_client, expense_dataset
) -> None:
    """EC-P1 valid: category filter limits report totals."""
    response = await integration_client.get(
        "/internal/v1/reports/monthly",
        params={"year": 2026, "category_id": expense_dataset["food_id"]},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["grand_total"] == "50.50"
    assert len(body["months"]) == 2
