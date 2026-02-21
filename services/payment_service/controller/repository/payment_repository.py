from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from services.payment_service.app.models import Member, Order, Product


def get_active_member_by_id(db: Session, member_id: int) -> Member | None:
    stmt = select(Member).where(Member.id == member_id, Member.delete_at.is_(None))
    return db.execute(stmt).scalar_one_or_none()


def get_active_product_by_id(db: Session, product_id: int) -> Product | None:
    stmt = select(Product).where(Product.id == product_id, Product.delete_at.is_(None))
    return db.execute(stmt).scalar_one_or_none()


def create_order(db: Session, member_id: int, product_id: int, amount: Decimal, currency: str) -> Order:
    order = Order(
        member_id=member_id,
        product_id=product_id,
        amount=amount,
        currency=currency,
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


def count_active_orders_by_product_id(db: Session, product_id: int) -> int:
    stmt = select(func.count(Order.id)).where(Order.product_id == product_id, Order.delete_at.is_(None))
    return int(db.execute(stmt).scalar_one())
