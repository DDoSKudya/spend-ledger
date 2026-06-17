import os

import pytest

pytestmark = pytest.mark.skipif(
    os.getenv("LEDGER_INTEGRATION", "").lower() not in {"1", "true", "yes"},
    reason="Set LEDGER_INTEGRATION=1 and LEDGER_DATABASE_URL for integration tests",
)


@pytest.mark.asyncio
async def test_category_crud_happy_path(integration_client) -> None:
    """EC-P0 valid: create -> list -> update -> delete category."""
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
async def test_delete_category_in_use_returns_409(integration_client) -> None:
    """EC-P0 invalid: category with expenses -> 409 category_in_use."""
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
async def test_expense_with_tags_persists_relations(integration_client) -> None:
    """EC-P0 valid: expense stores category and tags."""
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
    page = listed.json()
    assert page["total"] == 1
    assert len(page["items"]) == 1


@pytest.mark.asyncio
async def test_duplicate_category_name_returns_409(integration_client) -> None:
    """EC-P0 invalid: duplicate category name -> 409."""
    client = integration_client
    await client.post("/internal/v1/categories", json={"name": "Food"})
    response = await client.post("/internal/v1/categories", json={"name": "Food"})
    assert response.status_code == 409
    assert response.json()["code"] == "category_duplicate_name"


@pytest.mark.asyncio
async def test_missing_user_header_returns_401(integration_client_without_user_header) -> None:
    """EC-P0 invalid: missing X-User-Id -> 401."""
    response = await integration_client_without_user_header.get("/internal/v1/categories")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_foreign_expense_is_not_visible(
    integration_client, integration_client_user_b
) -> None:
    """EC-P0 invalid: other user's expense -> 404."""
    user_a = integration_client
    user_b = integration_client_user_b

    category = await user_a.post("/internal/v1/categories", json={"name": "Food"})
    category_id = category.json()["id"]
    created = await user_a.post(
        "/internal/v1/expenses",
        json={
            "amount": "15.00",
            "category_id": category_id,
            "tag_ids": [],
            "description": "for-a",
            "expense_date": "2026-06-16",
        },
    )
    expense_id = created.json()["id"]

    foreign_read = await user_b.get(f"/internal/v1/expenses/{expense_id}")
    assert foreign_read.status_code == 404


@pytest.mark.asyncio
async def test_tag_crud_happy_path(integration_client) -> None:
    """EC-P0 valid: create -> list -> get -> update -> delete tag."""
    client = integration_client
    create = await client.post("/internal/v1/tags", json={"name": "weekly"})
    assert create.status_code == 201
    tag_id = create.json()["id"]

    listed = await client.get("/internal/v1/tags")
    assert listed.status_code == 200
    assert len(listed.json()) == 1

    fetched = await client.get(f"/internal/v1/tags/{tag_id}")
    assert fetched.status_code == 200
    assert fetched.json()["name"] == "weekly"

    updated = await client.patch(
        f"/internal/v1/tags/{tag_id}",
        json={"name": "monthly"},
    )
    assert updated.status_code == 200
    assert updated.json()["name"] == "monthly"

    deleted = await client.delete(f"/internal/v1/tags/{tag_id}")
    assert deleted.status_code == 204


@pytest.mark.asyncio
async def test_duplicate_tag_name_returns_409(integration_client) -> None:
    """EC-P0 invalid: duplicate tag name -> 409."""
    client = integration_client
    await client.post("/internal/v1/tags", json={"name": "weekly"})
    response = await client.post("/internal/v1/tags", json={"name": "weekly"})
    assert response.status_code == 409
    assert response.json()["code"] == "tag_duplicate_name"


@pytest.mark.asyncio
async def test_expense_update_and_delete_happy_path(integration_client) -> None:
    """EC-P0 valid: update expense fields and delete."""
    client = integration_client
    category = await client.post("/internal/v1/categories", json={"name": "Food"})
    tag = await client.post("/internal/v1/tags", json={"name": "weekly"})
    category_id = category.json()["id"]
    tag_id = tag.json()["id"]

    created = await client.post(
        "/internal/v1/expenses",
        json={
            "amount": "10.00",
            "category_id": category_id,
            "tag_ids": [],
            "description": "coffee",
            "expense_date": "2026-06-10",
        },
    )
    expense_id = created.json()["id"]

    updated = await client.put(
        f"/internal/v1/expenses/{expense_id}",
        json={
            "amount": "12.50",
            "category_id": category_id,
            "tag_ids": [tag_id],
            "description": "coffee + pastry",
            "expense_date": "2026-06-11",
        },
    )
    assert updated.status_code == 200
    body = updated.json()
    assert body["amount"] == "12.50"
    assert body["description"] == "coffee + pastry"
    assert body["tags"][0]["name"] == "weekly"

    deleted = await client.delete(f"/internal/v1/expenses/{expense_id}")
    assert deleted.status_code == 204

    listed = await client.get("/internal/v1/expenses")
    assert listed.json()["total"] == 0


@pytest.mark.parametrize(
    ("method", "path"),
    [
        ("get", "/internal/v1/categories/00000000-0000-4000-8000-000000009999"),
        ("get", "/internal/v1/tags/00000000-0000-4000-8000-000000009999"),
        ("get", "/internal/v1/expenses/00000000-0000-4000-8000-000000009999"),
    ],
    ids=["category", "tag", "expense"],
)
@pytest.mark.asyncio
async def test_get_missing_resource_returns_404(integration_client, method, path) -> None:
    """EC-P0 invalid: unknown resource id -> 404."""
    response = await getattr(integration_client, method)(path)
    assert response.status_code == 404
