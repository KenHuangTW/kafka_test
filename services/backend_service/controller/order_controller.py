from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from common.cache_decorator import redis_function_cache
from services.backend_service.controller.repository import get_active_order_by_id, get_active_order_list
from services.backend_service.database import get_redis
from services.backend_service.schemas import OrderData, OrderGetResponse, OrderListResponse


@redis_function_cache(
    redis_getter=get_redis,
    ttl_seconds=120,
    prefix="backend:function:order",
    key_builder=lambda args: str(args["order_id"]),
    serializer=lambda value: value.model_dump_json(),
    deserializer=lambda raw: OrderGetResponse.model_validate_json(raw),
)
async def get_order(db: Session, order_id: int) -> OrderGetResponse:
    order = get_active_order_by_id(db=db, order_id=order_id)
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="order not found")
    return OrderGetResponse(
        success=True,
        message="get order success",
        data=OrderData.model_validate(order),
    )


@redis_function_cache(
    redis_getter=get_redis,
    ttl_seconds=120,
    prefix="backend:function:order:list",
    key_builder=lambda args: f"{args['limit']}:{args['offset']}",
    serializer=lambda value: value.model_dump_json(),
    deserializer=lambda raw: OrderListResponse.model_validate_json(raw),
)
async def get_order_list(db: Session, limit: int, offset: int) -> OrderListResponse:
    orders = get_active_order_list(db=db, limit=limit, offset=offset)
    return OrderListResponse(
        success=True,
        message="get order list success",
        data=[OrderData.model_validate(order) for order in orders],
    )
