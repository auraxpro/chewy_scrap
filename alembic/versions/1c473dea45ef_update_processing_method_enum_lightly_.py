"""update_processing_method_enum_lightly_cooked_frozen

Revision ID: 1c473dea45ef
Revises: 0d664726ee32
Create Date: 2025-12-10 21:36:11.184313

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "1c473dea45ef"
down_revision: Union[str, None] = "add_nutritionally_adequate_other"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Update the enum value from "Lightly Cooked + Frozen" to "Lightly Cooked (Frozen)"
    # Note: This may have already been applied, so check first
    try:
        op.execute("""
            DO $$ 
            BEGIN
                IF EXISTS (
                    SELECT 1 FROM pg_enum 
                    WHERE enumlabel = 'Lightly Cooked + Frozen' 
                    AND enumtypid = (SELECT oid FROM pg_type WHERE typname = 'processingmethodenum')
                ) THEN
                    ALTER TYPE processingmethodenum RENAME VALUE 'Lightly Cooked + Frozen' TO 'Lightly Cooked (Frozen)';
                END IF;
            EXCEPTION
                WHEN OTHERS THEN
                    -- If it fails, it's likely already renamed
                    NULL;
            END $$;
        """)
    except Exception as e:
        # If it fails, it's likely already applied
        print(f"Warning: Could not rename enum value (may already be renamed): {e}")


def downgrade() -> None:
    # Revert back to original value
    op.execute("""
        ALTER TYPE processingmethodenum RENAME VALUE 'Lightly Cooked (Frozen)' TO 'Lightly Cooked + Frozen';
    """)
