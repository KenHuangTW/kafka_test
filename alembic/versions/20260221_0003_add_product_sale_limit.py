"""add product sale limit

Revision ID: 20260221_0003
Revises: 20260217_0002
Create Date: 2026-02-21 00:00:00

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260221_0003"
down_revision: Union[str, None] = "20260217_0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "product",
        sa.Column("sale_limit", sa.Integer(), nullable=False, server_default=sa.text("2147483647")),
    )
    op.alter_column("product", "sale_limit", server_default=None)


def downgrade() -> None:
    op.drop_column("product", "sale_limit")
