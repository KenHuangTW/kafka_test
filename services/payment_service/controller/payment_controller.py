from decimal import Decimal
from datetime import UTC, datetime
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from common.kafka_client import KafkaManager
from services.payment_service.controller.repository.payment_repository import (
    count_active_orders_by_product_id,
    create_order,
    get_active_member_by_id,
    get_active_product_by_id,
)
from services.payment_service.schemas.payment import PaymentCheckoutRequest, PaymentCheckoutResponse, PaymentData
from services.payment_service.utils.jwt import decode_member_token


ProductSnapshot = dict[str, int | str | None]


async def _publish_order_created_event(kafka: KafkaManager, *, order_id: int) -> None:
    event = {
        "event_id": str(uuid4()),
        "event_type": "order.created",
        "entity": "order",
        "entity_id": str(order_id),
        "version": order_id,
        "updated_at": datetime.now(UTC).isoformat(),
        "trace_id": str(uuid4()),
    }

    try:
        await kafka.publish(event)
    except Exception:
        # Event bus failure should not block payment success.
        return


async def _get_product_snapshot(db: Session, product_id: int) -> ProductSnapshot | None:
    product = get_active_product_by_id(db=db, product_id=product_id)
    if product is None:
        return None
    return {
        "id": product.id,
        "price": product.price,
        "currency": product.currency,
        "sale_limit": product.sale_limit,
    }


async def _require_product(db: Session, product_id: int) -> ProductSnapshot:
    product = await _get_product_snapshot(db=db, product_id=product_id)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="product not found")
    return product


async def checkout_payment(
    db: Session,
    payload: PaymentCheckoutRequest,
    kafka: KafkaManager | None = None,
) -> PaymentCheckoutResponse:
    member_id = decode_member_token(payload.token)

    member = get_active_member_by_id(db=db, member_id=member_id)
    if member is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token")

    product = await _require_product(db=db, product_id=payload.product_id)
    sold_count = count_active_orders_by_product_id(db=db, product_id=int(product["id"]))
    sale_limit = product["sale_limit"]
    if sale_limit is not None and sold_count >= int(sale_limit):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="product sold out")

    order = create_order(
        db=db,
        member_id=member.id,
        product_id=int(product["id"]),
        amount=Decimal(int(product["price"])),
        currency=str(product["currency"]),
    )
    if kafka is not None:
        await _publish_order_created_event(kafka=kafka, order_id=order.id)

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
