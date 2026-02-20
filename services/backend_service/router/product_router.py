from fastapi import APIRouter

from services.backend_service.controller.product_controller import get_product
from services.backend_service.depend import DBSessionDep
from services.backend_service.schemas import ProductData

router = APIRouter(prefix="/product", tags=["product"])


@router.get("/{product_id}", response_model=ProductData)
async def get_product_by_id(product_id: int, db: DBSessionDep) -> ProductData:
    return await get_product(db=db, product_id=product_id)
