from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from common.cache_decorator import redis_function_cache
from services.backend_service.controller.repository import get_active_product_by_id, get_active_product_list
from services.backend_service.database import get_redis
from services.backend_service.schemas import ProductData, ProductGetResponse, ProductListResponse


@redis_function_cache(
    redis_getter=get_redis,
    ttl_seconds=120,
    prefix="backend:function:product",
    key_builder=lambda args: str(args["product_id"]),
    serializer=lambda value: value.model_dump_json(),
    deserializer=lambda raw: ProductGetResponse.model_validate_json(raw),
)
async def get_product(db: Session, product_id: int) -> ProductGetResponse:
    product = get_active_product_by_id(db=db, product_id=product_id)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="product not found")
    return ProductGetResponse(
        success=True,
        message="get product success",
        data=ProductData.model_validate(product),
    )


@redis_function_cache(
    redis_getter=get_redis,
    ttl_seconds=120,
    prefix="backend:function:product:list",
    key_builder=lambda args: f"{args['limit']}:{args['offset']}",
    serializer=lambda value: value.model_dump_json(),
    deserializer=lambda raw: ProductListResponse.model_validate_json(raw),
)
async def get_product_list(db: Session, limit: int, offset: int) -> ProductListResponse:
    products = get_active_product_list(db=db, limit=limit, offset=offset)
    return ProductListResponse(
        success=True,
        message="get product list success",
        data=[ProductData.model_validate(product) for product in products],
    )
