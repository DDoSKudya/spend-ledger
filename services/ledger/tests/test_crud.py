import os

import pytest

pytestmark = pytest.mark.skipif(
    os.getenv("LEDGER_INTEGRATION", "").lower() not in {"1", "true", "yes"},
    reason="Set LEDGER_INTEGRATION=1 and LEDGER_DATABASE_URL for integration tests",
)


@pytest.mark.asyncio
async def test_category_crud(integration_client):
    client = integration_client
    create = await client.post("/internal/v1/categories", json={"name": "Food"})
    assert create.status_code == 201
    category_id = create.json()["id"]

    listed = await client.get("/internal/v1/categories")
    assert listed.status_code == 200
    assert len(listed.json()) == 1

    updated = await client.put(
        f"/internal/v1/categories/{category_id}",
        json={"name": "Groceries"},
    )
    assert updated.status_code == 200
    assert updated.json()["name"] == "Groceries"

    deleted = await client.delete(f"/internal/v1/categories/{category_id}")
    assert deleted.status_code == 204


@pytest.mark.asyncio
async def test_delete_category_in_use_returns_409(integration_client):
    client = integration_client
    category = await client.post("/internal/v1/categories", json={"name": "Food"})
    category_id = category.json()["id"]
    await client.post(
        "/internal/v1/expenses",
        json={
            "amount": "10.00",
            "category_id": category_id,
            "tag_ids": [],
            "description": "milk",
            "expense_date": "2026-06-15",
        },
    )

    response = await client.delete(f"/internal/v1/categories/{category_id}")
    assert response.status_code == 409
    assert response.json()["code"] == "category_in_use"


@pytest.mark.asyncio
async def test_expense_with_tags(integration_client):
    client = integration_client
    category = await client.post("/internal/v1/categories", json={"name": "Food"})
    tag = await client.post("/internal/v1/tags", json={"name": "weekly"})
    category_id = category.json()["id"]
    tag_id = tag.json()["id"]

    created = await client.post(
        "/internal/v1/expenses",
        json={
            "amount": "42.50",
            "category_id": category_id,
            "tag_ids": [tag_id],
            "description": "groceries",
            "expense_date": "2026-06-15",
        },
    )
    assert created.status_code == 201
    body = created.json()
    assert body["amount"] == "42.50"
    assert body["category"]["name"] == "Food"
    assert body["tags"][0]["name"] == "weekly"

    listed = await client.get("/internal/v1/expenses")
    assert listed.status_code == 200
    assert len(listed.json()) == 1


@pytest.mark.asyncio
async def test_duplicate_category_name_returns_409(integration_client):
    client = integration_client
    await client.post("/internal/v1/categories", json={"name": "Food"})
    response = await client.post("/internal/v1/categories", json={"name": "Food"})
    assert response.status_code == 409
    assert response.json()["code"] == "category_duplicate_name"
