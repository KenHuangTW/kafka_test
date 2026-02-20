from decimal import Decimal

from pydantic import BaseModel, Field

from .base import BaseResponse


class PaymentCheckoutRequest(BaseModel):
    token: str = Field(min_length=1)
    product_id: int


class PaymentData(BaseModel):
    order_id: int
    member_id: int
    product_id: int
    amount: Decimal
    currency: str


class PaymentCheckoutResponse(BaseResponse):
    data: PaymentData
