"""add product price and currency

Revision ID: 20260217_0002
Revises: 20260216_0001
Create Date: 2026-02-17 00:00:00

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260217_0002"
down_revision: Union[str, None] = "20260216_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "product",
        sa.Column("price", sa.Integer(), nullable=False, server_default=sa.text("0")),
    )
    op.add_column(
        "product",
        sa.Column("currency", sa.String(length=8), nullable=False, server_default=sa.text("'TWD'")),
    )
    op.alter_column("product", "price", server_default=None)
    op.alter_column("product", "currency", server_default=None)


def downgrade() -> None:
    op.drop_column("product", "currency")
    op.drop_column("product", "price")
