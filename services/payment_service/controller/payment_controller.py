from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from common.cache_decorator import redis_function_cache
from services.payment_service.controller.repository.payment_repository import (
    create_order,
    get_active_member_by_id,
    get_active_product_by_id,
)
from services.payment_service.database import get_redis
from services.payment_service.schemas.payment import PaymentCheckoutRequest, PaymentCheckoutResponse, PaymentData
from services.payment_service.utils.jwt import decode_member_token


@redis_function_cache(
    redis_getter=get_redis,
    ttl_seconds=120,
    prefix="payment:function:product",
    key_builder=lambda args: str(args["product_id"]),
)
async def _get_product_snapshot(db: Session, product_id: int) -> dict[str, int | str] | None:
    product = get_active_product_by_id(db=db, product_id=product_id)
    if product is None:
        return None
    return {"id": product.id, "price": product.price, "currency": product.currency}


async def _require_product(db: Session, product_id: int) -> dict[str, int | str]:
    product = await _get_product_snapshot(db=db, product_id=product_id)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="product not found")
    return product


async def checkout_payment(db: Session, payload: PaymentCheckoutRequest) -> PaymentCheckoutResponse:
    member_id = decode_member_token(payload.token)

    member = get_active_member_by_id(db=db, member_id=member_id)
    if member is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token")

    product = await _require_product(db=db, product_id=payload.product_id)

    order = create_order(
        db=db,
        member_id=member.id,
        product_id=int(product["id"]),
        amount=Decimal(int(product["price"])),
        currency=str(product["currency"]),
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
