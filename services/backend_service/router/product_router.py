from fastapi import APIRouter, Query
from services.backend_service.controller.product_controller import (
    get_product,
    get_product_list,
)
from services.backend_service.depend import DBSessionDep
from services.backend_service.schemas import ProductGetResponse, ProductListResponse

router = APIRouter(prefix="/product", tags=["product"])


@router.get("/", response_model=ProductListResponse)
async def get_products(
    db: DBSessionDep,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> ProductListResponse:
    return await get_product_list(db=db, limit=limit, offset=offset)


@router.get("/{product_id}", response_model=ProductGetResponse)
async def get_product_by_id(
    product_id: int,
    db: DBSessionDep,
) -> ProductGetResponse:
    return await get_product(db=db, product_id=product_id)
