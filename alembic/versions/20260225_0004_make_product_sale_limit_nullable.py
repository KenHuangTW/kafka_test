"""make product sale_limit nullable

Revision ID: 20260225_0004
Revises: 20260221_0003
Create Date: 2026-02-25 00:00:00

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260225_0004"
down_revision: Union[str, None] = "20260221_0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("product", "sale_limit", existing_type=sa.Integer(), nullable=True)


def downgrade() -> None:
    op.execute("UPDATE product SET sale_limit = 2147483647 WHERE sale_limit IS NULL")
    op.alter_column("product", "sale_limit", existing_type=sa.Integer(), nullable=False)
