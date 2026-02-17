from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from services.main_service.app.models import Product
from services.main_service.controller.repository.product_repository import (
    create_product,
    get_active_product_by_id,
    soft_delete_product,
    update_product,
)
from services.main_service.schemas.product import ProductActionResponse, ProductData, ProductUpsertRequest


def _require_product(db: Session, product_id: int) -> Product:
    product = get_active_product_by_id(db=db, product_id=product_id)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="product not found")
    return product


async def get_product(db: Session, product_id: int) -> ProductData:
    product = _require_product(db=db, product_id=product_id)
    return ProductData.model_validate(product)


async def create_new_product(db: Session, payload: ProductUpsertRequest) -> ProductData:
    product = create_product(
        db=db,
        name=payload.name,
        description=payload.description,
        price=payload.price,
        currency=payload.currency,
    )
    return ProductData.model_validate(product)


async def update_existing_product(db: Session, product_id: int, payload: ProductUpsertRequest) -> ProductActionResponse:
    product = _require_product(db=db, product_id=product_id)
    update_product(
        db=db,
        product=product,
        name=payload.name,
        description=payload.description,
        price=payload.price,
        currency=payload.currency,
    )
    return ProductActionResponse(success=True)


async def delete_product(db: Session, product_id: int) -> ProductActionResponse:
    product = _require_product(db=db, product_id=product_id)
    soft_delete_product(db=db, product=product)
    return ProductActionResponse(success=True)
