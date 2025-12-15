"""add_brand_fields_to_processed_products

Revision ID: b7c8d9e0f1a2
Revises: a1b2c3d4e5f6
Create Date: 2025-01-15 14:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b7c8d9e0f1a2"
down_revision: Union[str, None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add brand fields to processed_products table
    op.execute("""
        ALTER TABLE processed_products
        ADD COLUMN IF NOT EXISTS brand VARCHAR;
    """)
    op.execute("""
        ALTER TABLE processed_products
        ADD COLUMN IF NOT EXISTS brand_detection_method VARCHAR;
    """)
    op.execute("""
        ALTER TABLE processed_products
        ADD COLUMN IF NOT EXISTS brand_detection_confidence VARCHAR;
    """)
    op.execute("""
        ALTER TABLE processed_products
        ADD COLUMN IF NOT EXISTS brand_detection_reason TEXT;
    """)


def downgrade() -> None:
    # Remove the brand fields
    op.execute("""
        ALTER TABLE processed_products
        DROP COLUMN IF EXISTS brand_detection_reason;
    """)
    op.execute("""
        ALTER TABLE processed_products
        DROP COLUMN IF EXISTS brand_detection_confidence;
    """)
    op.execute("""
        ALTER TABLE processed_products
        DROP COLUMN IF EXISTS brand_detection_method;
    """)
    op.execute("""
        ALTER TABLE processed_products
        DROP COLUMN IF EXISTS brand;
    """)

