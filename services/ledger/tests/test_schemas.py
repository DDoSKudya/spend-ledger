from decimal import Decimal

from app.core.schemas import serialize_amount


def test_serialize_amount_two_decimals() -> None:
    assert serialize_amount(Decimal("42.5")) == "42.50"
    assert serialize_amount(Decimal("42.50")) == "42.50"
