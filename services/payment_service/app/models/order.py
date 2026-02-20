from datetime import datetime
from decimal import Decimal

from sqlalchemy import Numeric, String, text
from sqlalchemy.dialects import mysql
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(mysql.BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    member_id: Mapped[int] = mapped_column(mysql.BIGINT(unsigned=True), nullable=False)
    product_id: Mapped[int] = mapped_column(mysql.BIGINT(unsigned=True), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(8), nullable=False)
    create_at: Mapped[datetime] = mapped_column(
        mysql.TIMESTAMP(), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    update_at: Mapped[datetime] = mapped_column(
        mysql.TIMESTAMP(),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
    )
    delete_at: Mapped[datetime | None] = mapped_column(mysql.TIMESTAMP(), nullable=True)
