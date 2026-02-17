from datetime import datetime

from sqlalchemy import String, Text, text
from sqlalchemy.dialects import mysql
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Product(Base):
    __tablename__ = "product"

    id: Mapped[int] = mapped_column(mysql.BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str | None] = mapped_column(Text(), nullable=True)
    price: Mapped[int] = mapped_column(nullable=False)
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
