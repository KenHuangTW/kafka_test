from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from services.main_service.app.models import Product


def get_active_product_by_id(db: Session, product_id: int) -> Product | None:
    stmt = select(Product).where(Product.id == product_id, Product.delete_at.is_(None))
    return db.execute(stmt).scalar_one_or_none()


def create_product(
    db: Session,
    name: str,
    description: str | None,
    price: int,
    currency: str,
    sale_limit: int | None,
) -> Product:
    product = Product(
        name=name,
        description=description,
        price=price,
        currency=currency,
        sale_limit=sale_limit,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def update_product(
    db: Session,
    product: Product,
    name: str,
    description: str | None,
    price: int,
    currency: str,
    sale_limit: int | None,
) -> Product:
    product.name = name
    product.description = description
    product.price = price
    product.currency = currency
    product.sale_limit = sale_limit
    db.commit()
    db.refresh(product)
    return product


def soft_delete_product(db: Session, product: Product) -> Product:
    product.delete_at = datetime.utcnow()
    db.commit()
    db.refresh(product)
    return product
