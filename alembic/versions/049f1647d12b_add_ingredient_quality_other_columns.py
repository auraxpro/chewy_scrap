"""add_ingredient_quality_other_columns

Revision ID: 049f1647d12b
Revises: 1c473dea45ef
Create Date: 2025-12-10 23:29:49.329996

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "049f1647d12b"
down_revision: Union[str, None] = "1c473dea45ef"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add "Other" to qualityclassenum
    # Note: ALTER TYPE ADD VALUE may need to run outside transaction
    # If this fails, run the SQL manually: add_other_enum_value.sql
    try:
        op.execute("""
            DO $$ 
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_enum 
                    WHERE enumlabel = 'Other' 
                    AND enumtypid = (SELECT oid FROM pg_type WHERE typname = 'qualityclassenum')
                ) THEN
                    ALTER TYPE qualityclassenum ADD VALUE 'Other';
                END IF;
            EXCEPTION
                WHEN duplicate_object THEN
                    NULL;
            END $$;
        """)
    except Exception as e:
        # If it fails due to transaction issues, print helpful message
        print(f"Warning: Could not add 'Other' to enum automatically: {e}")
        print("Please run the SQL manually from add_other_enum_value.sql")
        raise
    
    # Add missing ingredient quality "other" columns
    op.execute("""
        ALTER TABLE processed_products
        ADD COLUMN IF NOT EXISTS protein_ingredients_other TEXT,
        ADD COLUMN IF NOT EXISTS fat_ingredients_other TEXT,
        ADD COLUMN IF NOT EXISTS carb_ingredients_other TEXT,
        ADD COLUMN IF NOT EXISTS fiber_ingredients_other TEXT;
    """)


def downgrade() -> None:
    # Remove the added columns
    op.execute("""
        ALTER TABLE processed_products
        DROP COLUMN IF EXISTS protein_ingredients_other,
        DROP COLUMN IF EXISTS fat_ingredients_other,
        DROP COLUMN IF EXISTS carb_ingredients_other,
        DROP COLUMN IF EXISTS fiber_ingredients_other;
    """)
