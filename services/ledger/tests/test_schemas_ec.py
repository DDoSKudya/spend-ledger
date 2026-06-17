from datetime import date
from decimal import Decimal
from uuid import UUID

import pytest
from pydantic import ValidationError as PydanticValidationError

from app.core.exceptions import ValidationError
from app.core.pagination import build_page, compute_pages
from app.core.schemas import serialize_amount
from app.expenses.schemas import ExpenseCreate
from app.expenses.service import parse_sort

TEST_CATEGORY_ID = UUID("11111111-1111-1111-1111-111111111111")
TEST_EXPENSE_DATE = date(2026, 6, 15)


@pytest.mark.parametrize(
    ("amount", "expected"),
    [
        (Decimal("42.5"), "42.50"),
        (Decimal("42.50"), "42.50"),
        (Decimal("0.01"), "0.01"),
    ],
    ids=["single-decimal", "two-decimals", "boundary-min-positive"],
)
def test_serialize_amount_valid_positive_values(amount: Decimal, expected: str) -> None:
    """EC-P0 valid: amount > 0 -> two-decimal string."""
    assert serialize_amount(amount) == expected


@pytest.mark.parametrize(
    "amount",
    [Decimal("0"), Decimal("-1")],
    ids=["zero", "negative"],
)
def test_expense_create_rejects_non_positive_amount(amount: Decimal) -> None:
    """EC-P0 invalid: amount <= 0 -> validation error."""
    with pytest.raises(PydanticValidationError):
        ExpenseCreate(
            amount=amount,
            category_id=TEST_CATEGORY_ID,
            expense_date=TEST_EXPENSE_DATE,
        )


@pytest.mark.parametrize(
    ("total", "size", "expected_pages"),
    [
        (0, 20, 0),
        (1, 20, 1),
        (20, 20, 1),
        (21, 20, 2),
    ],
    ids=["empty", "single-page-first", "exact-page", "needs-second-page"],
)
def test_compute_pages_boundary_values(total: int, size: int, expected_pages: int) -> None:
    """EC-P0 boundary: pagination page count."""
    assert compute_pages(total, size) == expected_pages


def test_build_page_returns_expected_shape() -> None:
    """EC-P0 valid: page object contains items and metadata."""
    page = build_page(["a", "b"], total=2, page=1, size=20)
    assert page.items == ["a", "b"]
    assert page.total == 2
    assert page.page == 1
    assert page.size == 20
    assert page.pages == 1


@pytest.mark.parametrize(
    ("sort", "field", "desc"),
    [
        ("amount:asc", "amount", False),
        ("expense_date:desc", "expense_date", True),
    ],
    ids=["amount-asc", "date-desc"],
)
def test_parse_sort_valid_classes(sort: str, field: str, desc: bool) -> None:
    """EC-P0 valid: sort field:direction parses to column and order."""
    assert parse_sort(sort) == (field, desc)


@pytest.mark.parametrize(
    "sort",
    ["invalid", "amount:up", "bad:asc"],
    ids=["missing-colon", "bad-direction", "bad-field"],
)
def test_parse_sort_invalid_classes(sort: str) -> None:
    """EC-P0 invalid: malformed sort -> ValidationError."""
    with pytest.raises(ValidationError):
        parse_sort(sort)
