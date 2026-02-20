from datetime import datetime

from sqlalchemy import String, text
from sqlalchemy.dialects import mysql
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Member(Base):
    __tablename__ = "member"

    id: Mapped[int] = mapped_column(mysql.BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    account: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    create_at: Mapped[datetime] = mapped_column(
        mysql.TIMESTAMP(), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    update_at: Mapped[datetime] = mapped_column(
        mysql.TIMESTAMP(),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
    )
    delete_at: Mapped[datetime | None] = mapped_column(mysql.TIMESTAMP(), nullable=True)
