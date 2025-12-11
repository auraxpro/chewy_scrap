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
down_revision: Union[str, None] = "0d664726ee32"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Update the enum value from "Lightly Cooked + Frozen" to "Lightly Cooked (Frozen)"
    op.execute("""
        ALTER TYPE processingmethodenum RENAME VALUE 'Lightly Cooked + Frozen' TO 'Lightly Cooked (Frozen)';
    """)


def downgrade() -> None:
    # Revert back to original value
    op.execute("""
        ALTER TYPE processingmethodenum RENAME VALUE 'Lightly Cooked (Frozen)' TO 'Lightly Cooked + Frozen';
    """)
