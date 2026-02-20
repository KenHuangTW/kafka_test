from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from services.payment_service.controller.repository.payment_repository import (
    create_order,
    get_active_member_by_id,
    get_active_product_by_id,
)
from services.payment_service.schemas.payment import PaymentCheckoutRequest, PaymentCheckoutResponse, PaymentData
from services.payment_service.utils.jwt import decode_member_token


def _require_product(db: Session, product_id: int):
    product = get_active_product_by_id(db=db, product_id=product_id)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="product not found")
    return product


async def checkout_payment(db: Session, payload: PaymentCheckoutRequest) -> PaymentCheckoutResponse:
    member_id = decode_member_token(payload.token)

    member = get_active_member_by_id(db=db, member_id=member_id)
    if member is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token")

    product = _require_product(db=db, product_id=payload.product_id)

    order = create_order(
        db=db,
        member_id=member.id,
        product_id=product.id,
        amount=Decimal(product.price),
        currency=product.currency,
    )
    return PaymentCheckoutResponse(
        success=True,
        message="payment success",
        data=PaymentData(
            order_id=order.id,
            member_id=order.member_id,
            product_id=order.product_id,
            amount=order.amount,
            currency=order.currency,
        ),
    )
