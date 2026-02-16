"""init schema

Revision ID: 20260216_0001
Revises:
Create Date: 2026-02-16 00:00:00

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = "20260216_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "member",
        sa.Column("id", mysql.BIGINT(unsigned=True), primary_key=True, autoincrement=True),
        sa.Column("account", sa.String(length=128), nullable=False),
        sa.Column("password", sa.String(length=255), nullable=False),
        sa.Column("create_at", sa.TIMESTAMP(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column(
            "update_at",
            sa.TIMESTAMP(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
        ),
        sa.Column("delete_at", sa.TIMESTAMP(), nullable=True),
    )
    op.create_unique_constraint("uk_member_account", "member", ["account"])

    op.create_table(
        "product",
        sa.Column("id", mysql.BIGINT(unsigned=True), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("create_at", sa.TIMESTAMP(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column(
            "update_at",
            sa.TIMESTAMP(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
        ),
        sa.Column("delete_at", sa.TIMESTAMP(), nullable=True),
    )
    op.create_table(
        "orders",
        sa.Column("id", mysql.BIGINT(unsigned=True), primary_key=True, autoincrement=True),
        sa.Column("member_id", mysql.BIGINT(unsigned=True), nullable=False),
        sa.Column("product_id", mysql.BIGINT(unsigned=True), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("currency", sa.String(length=8), nullable=False),
        sa.Column("create_at", sa.TIMESTAMP(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column(
            "update_at",
            sa.TIMESTAMP(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
        ),
        sa.Column("delete_at", sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(["member_id"], ["member.id"], name="fk_orders_member_id"),
        sa.ForeignKeyConstraint(["product_id"], ["product.id"], name="fk_orders_product_id"),
    )
    op.create_index("idx_orders_member_id", "orders", ["member_id"])
    op.create_index("idx_orders_product_id", "orders", ["product_id"])


def downgrade() -> None:
    op.drop_index("idx_orders_product_id", table_name="orders")
    op.drop_index("idx_orders_member_id", table_name="orders")
    op.drop_table("orders")
    op.drop_table("product")
    op.drop_constraint("uk_member_account", "member", type_="unique")
    op.drop_table("member")
