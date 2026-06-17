import os
from datetime import date
from uuid import UUID

import pytest
from sqlalchemy import text

pytestmark = pytest.mark.skipif(
    os.getenv("LEDGER_INTEGRATION", "").lower() not in {"1", "true", "yes"},
    reason="Set LEDGER_INTEGRATION=1 and LEDGER_DATABASE_URL for integration tests",
)


@pytest.fixture
async def expense_dataset(integration_client):
    client = integration_client
    food = (await client.post("/internal/v1/categories", json={"name": "Food"})).json()
    transport = (await client.post("/internal/v1/categories", json={"name": "Transport"})).json()
    weekly = (await client.post("/internal/v1/tags", json={"name": "weekly"})).json()
    urgent = (await client.post("/internal/v1/tags", json={"name": "urgent"})).json()

    async def add_expense(**payload):
        response = await client.post("/internal/v1/expenses", json=payload)
        assert response.status_code == 201
        return response.json()

    groceries = await add_expense(
        amount="42.50",
        category_id=food["id"],
        tag_ids=[weekly["id"]],
        description="groceries",
        expense_date="2026-06-15",
    )
    taxi = await add_expense(
        amount="15.00",
        category_id=transport["id"],
        tag_ids=[urgent["id"]],
        description="taxi ride",
        expense_date="2026-06-20",
    )
    lunch = await add_expense(
        amount="8.00",
        category_id=food["id"],
        tag_ids=[weekly["id"], urgent["id"]],
        description="lunch",
        expense_date="2026-07-01",
    )

    return {
        "food_id": food["id"],
        "transport_id": transport["id"],
        "weekly_id": weekly["id"],
        "urgent_id": urgent["id"],
        "groceries_id": groceries["id"],
        "taxi_id": taxi["id"],
        "lunch_id": lunch["id"],
    }


@pytest.mark.asyncio
async def test_list_expenses_default_pagination(integration_client, expense_dataset):
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
)
async def test_list_expenses_filters(
    integration_client,
    expense_dataset,
    params,
    expected_ids_key,
):
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
async def test_list_expenses_tag_filter_or_semantics(integration_client, expense_dataset):
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
async def test_list_expenses_pagination(integration_client, expense_dataset):
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
async def test_list_expenses_invalid_sort(integration_client, expense_dataset):
    response = await integration_client.get(
        "/internal/v1/expenses",
        params={"sort": "invalid:desc"},
    )
    assert response.status_code == 422
    assert response.json()["code"] == "validation_error"


@pytest.mark.asyncio
async def test_monthly_report(integration_client, expense_dataset):
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
async def test_monthly_report_category_filter(integration_client, expense_dataset):
    response = await integration_client.get(
        "/internal/v1/reports/monthly",
        params={"year": 2026, "category_id": expense_dataset["food_id"]},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["grand_total"] == "50.50"
    assert len(body["months"]) == 2


TEST_USER_ID = "00000000-0000-4000-8000-000000000001"


@pytest.mark.asyncio
async def test_expense_list_uses_user_expense_date_index(
    integration_client,
    engine,
    expense_dataset,
):
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
