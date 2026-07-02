import os
from datetime import date
from uuid import UUID

import pytest
from sqlalchemy import text

pytestmark = pytest.mark.skipif(
    os.getenv("LEDGER_INTEGRATION", "").lower() not in {"1", "true", "yes"},
    reason="Set LEDGER_INTEGRATION=1 and LEDGER_DATABASE_URL for integration tests",
)


@pytest.mark.asyncio
async def test_list_expenses_default_pagination(integration_client, expense_dataset) -> None:
    """EC-P1 valid: default page returns all items sorted by date desc."""
    response = await integration_client.get("/internal/v1/expenses")
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 3
    assert body["page"] == 1
    assert body["size"] == 20
    assert body["pages"] == 1
    assert len(body["items"]) == 3
    assert body["items"][0]["expense_date"] == "2026-07-01"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("params", "expected_ids_key"),
    [
        ({"category_id": "food_id"}, ["lunch_id", "groceries_id"]),
        ({"tag_ids": "urgent_id"}, ["lunch_id", "taxi_id"]),
        ({"date_from": "2026-06-16", "date_to": "2026-06-30"}, ["taxi_id"]),
        ({"search": "grocer"}, ["groceries_id"]),
        ({"sort": "amount:asc", "size": 1, "page": 1}, ["lunch_id"]),
    ],
    ids=["category", "single-tag", "date-range", "search", "sort-page"],
)
async def test_list_expenses_filter_classes(
    integration_client,
    expense_dataset,
    params,
    expected_ids_key,
) -> None:
    """EC-P1 valid: each filter class returns expected expense ids."""
    resolved = {
        key: (expense_dataset[value] if isinstance(value, str) and value.endswith("_id") else value)
        for key, value in params.items()
    }
    if "tag_ids" in resolved:
        resolved["tag_ids"] = [resolved.pop("tag_ids")]

    response = await integration_client.get("/internal/v1/expenses", params=resolved)
    assert response.status_code == 200
    body = response.json()
    expected = {expense_dataset[key] for key in expected_ids_key}
    assert {item["id"] for item in body["items"]} == expected


@pytest.mark.asyncio
async def test_list_expenses_tag_filter_uses_or_semantics(
    integration_client, expense_dataset
) -> None:
    """EC-P1 valid: multiple tag_ids use OR semantics."""
    response = await integration_client.get(
        "/internal/v1/expenses",
        params={
            "tag_ids": [expense_dataset["weekly_id"], expense_dataset["urgent_id"]],
        },
    )
    assert response.status_code == 200
    ids = {item["id"] for item in response.json()["items"]}
    assert ids == {
        expense_dataset["groceries_id"],
        expense_dataset["taxi_id"],
        expense_dataset["lunch_id"],
    }


@pytest.mark.asyncio
async def test_list_expenses_pagination_second_page(integration_client, expense_dataset) -> None:
    """EC-P1 boundary: page 2 with size 2 returns remaining item."""
    response = await integration_client.get(
        "/internal/v1/expenses",
        params={"size": 2, "page": 2, "sort": "expense_date:asc"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 3
    assert body["pages"] == 2
    assert len(body["items"]) == 1
    assert body["items"][0]["id"] == expense_dataset["lunch_id"]


@pytest.mark.asyncio
async def test_list_expenses_invalid_sort_returns_422(integration_client, expense_dataset) -> None:
    """EC-P0 invalid: unknown sort field -> 422 validation_error."""
    response = await integration_client.get(
        "/internal/v1/expenses",
        params={"sort": "invalid:desc"},
    )
    assert response.status_code == 422
    assert response.json()["code"] == "validation_error"


TEST_USER_ID = "00000000-0000-4000-8000-000000000001"


@pytest.mark.asyncio
async def test_list_expenses_sql_query_count_bounded(
    integration_client,
    engine,
    expense_dataset,
) -> None:
    """EC-P1: list page loads relations without N+1 (count + page + tag batch)."""
    from app.core.deps import get_sql_count, reset_sql_count
    from app.core.sql_counter import attach_sql_counter

    attach_sql_counter(engine.sync_engine)
    reset_sql_count()

    response = await integration_client.get("/internal/v1/expenses?size=50")
    assert response.status_code == 200
    assert len(response.json()["items"]) >= 3

    sql_queries = get_sql_count()
    assert sql_queries <= 4, f"expected bounded queries for list page, got {sql_queries}"


@pytest.mark.asyncio
async def test_get_expense_sql_query_count_bounded(
    integration_client,
    engine,
    expense_dataset,
) -> None:
    """EC-P1: expense detail loads relations without N+1."""
    from app.core.deps import get_sql_count, reset_sql_count
    from app.core.sql_counter import attach_sql_counter

    attach_sql_counter(engine.sync_engine)
    reset_sql_count()

    expense_id = expense_dataset["groceries_id"]
    response = await integration_client.get(f"/internal/v1/expenses/{expense_id}")
    assert response.status_code == 200
    body = response.json()
    assert body["category"]["name"] == "Food"
    assert body["tags"]

    sql_queries = get_sql_count()
    assert sql_queries <= 2, f"expected bounded queries for expense detail, got {sql_queries}"


@pytest.mark.asyncio
async def test_expense_list_uses_user_expense_date_index(
    integration_client,
    engine,
    expense_dataset,
) -> None:
    """EC-P2: query plan uses expense_date index."""
    async with engine.connect() as conn:
        result = await conn.execute(
            text(
                "EXPLAIN SELECT id FROM expenses "
                "WHERE user_id = :user_id AND expense_date >= :date_from "
                "ORDER BY expense_date DESC"
            ),
            {"user_id": UUID(TEST_USER_ID), "date_from": date(2026, 6, 1)},
        )
        plan = "\n".join(row[0] for row in result)
    assert "idx_expenses_user_expense_date" in plan
