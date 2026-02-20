from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from common.cache_decorator import redis_function_cache
from services.backend_service.controller.repository import get_active_order_by_id
from services.backend_service.database import get_redis
from services.backend_service.schemas import OrderData


@redis_function_cache(
    redis_getter=get_redis,
    ttl_seconds=120,
    prefix="backend:function:order",
    key_builder=lambda args: str(args["order_id"]),
    serializer=lambda value: value.model_dump_json(),
    deserializer=lambda raw: OrderData.model_validate_json(raw),
)
async def get_order(db: Session, order_id: int) -> OrderData:
    order = get_active_order_by_id(db=db, order_id=order_id)
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="order not found")
    return OrderData.model_validate(order)
