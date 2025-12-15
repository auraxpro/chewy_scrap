"""add_base_score_column

Revision ID: a1b2c3d4e5f6
Revises: 049f1647d12b
Create Date: 2025-01-15 12:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "049f1647d12b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add base_score column to processed_products table
    op.execute("""
        ALTER TABLE processed_products
        ADD COLUMN IF NOT EXISTS base_score NUMERIC(5, 2);
    """)


def downgrade() -> None:
    # Remove the base_score column
    op.execute("""
        ALTER TABLE processed_products
        DROP COLUMN IF EXISTS base_score;
    """)

