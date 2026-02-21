from sqlalchemy import select
from sqlalchemy.orm import Session

from services.payment_service.app.models import Order, Product


def get_active_product_by_id(db: Session, product_id: int) -> Product | None:
    stmt = select(Product).where(Product.id == product_id, Product.delete_at.is_(None))
    return db.execute(stmt).scalar_one_or_none()


def get_active_product_list(db: Session, limit: int, offset: int) -> list[Product]:
    stmt = (
        select(Product)
        .where(Product.delete_at.is_(None))
        .order_by(Product.id.asc())
        .offset(offset)
        .limit(limit)
    )
    return list(db.execute(stmt).scalars().all())


def get_active_order_by_id(db: Session, order_id: int) -> Order | None:
    stmt = select(Order).where(Order.id == order_id, Order.delete_at.is_(None))
    return db.execute(stmt).scalar_one_or_none()


def get_active_order_list(db: Session, limit: int, offset: int) -> list[Order]:
    stmt = (
        select(Order)
        .where(Order.delete_at.is_(None))
        .order_by(Order.id.asc())
        .offset(offset)
        .limit(limit)
    )
    return list(db.execute(stmt).scalars().all())
