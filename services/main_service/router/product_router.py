from common.cache_decorator import redis_api_cache
from fastapi import APIRouter
from services.main_service.controller.product_controller import (
    create_new_product,
    delete_product,
    get_product,
    update_existing_product,
)
from services.main_service.database import get_redis
from services.main_service.depend import DBSessionDep
from services.main_service.schemas.product import (
    ProductActionResponse,
    ProductData,
    ProductUpsertRequest,
)

router = APIRouter(prefix="/product", tags=["product"])


@router.get("/{product_id}", response_model=ProductData)
@redis_api_cache(
    redis_getter=get_redis,
    ttl_seconds=120,
    prefix="main:api:product",
    key_builder=lambda args: str(args["product_id"]),
    serializer=lambda value: value.model_dump_json(),
    deserializer=lambda raw: ProductData.model_validate_json(raw),
)
async def get_product_by_id(product_id: int, db: DBSessionDep) -> ProductData:
    return await get_product(db=db, product_id=product_id)


@router.post("/", response_model=ProductData)
async def create_product(
    payload: ProductUpsertRequest, db: DBSessionDep
) -> ProductData:
    return await create_new_product(db=db, payload=payload)


@router.put("/{product_id}", response_model=ProductActionResponse)
async def update_product(
    product_id: int, payload: ProductUpsertRequest, db: DBSessionDep
) -> ProductActionResponse:
    return await update_existing_product(db=db, product_id=product_id, payload=payload)


@router.delete("/{product_id}", response_model=ProductActionResponse)
async def remove_product(product_id: int, db: DBSessionDep) -> ProductActionResponse:
    return await delete_product(db=db, product_id=product_id)
