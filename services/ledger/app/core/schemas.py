from decimal import Decimal

from pydantic import BaseModel, Field, field_serializer


def serialize_amount(value: Decimal) -> str:
    return format(value.quantize(Decimal("0.01")), "f")


class AmountMixin(BaseModel):
    amount: Decimal = Field(gt=0)

    @field_serializer("amount")
    def serialize_amount_field(self, value: Decimal) -> str:
        return serialize_amount(value)
