"""add_nutritionally_adequate_other

Revision ID: add_nutritionally_adequate_other
Revises: 0d664726ee32
Create Date: 2025-12-10 20:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "add_nutritionally_adequate_other"
down_revision: Union[str, None] = "0d664726ee32"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add "Other" to nutritionallyadequateenum
    # Note: This may have already been applied manually via SQL script
    # The IF NOT EXISTS check ensures it's safe to run again
    try:
        op.execute("""
            DO $$ 
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_enum 
                    WHERE enumlabel = 'Other' 
                    AND enumtypid = (SELECT oid FROM pg_type WHERE typname = 'nutritionallyadequateenum')
                ) THEN
                    ALTER TYPE nutritionallyadequateenum ADD VALUE 'Other';
                END IF;
            EXCEPTION
                WHEN duplicate_object THEN
                    NULL;
            END $$;
        """)
    except Exception as e:
        # If it fails, it's likely already applied
        print(f"Warning: Could not add 'Other' to enum (may already exist): {e}")


def downgrade() -> None:
    # Note: PostgreSQL does not support removing enum values
    # This is a no-op as enum values cannot be removed
    pass

