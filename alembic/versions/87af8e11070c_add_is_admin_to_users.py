"""add is_admin to users

Revision ID: 87af8e11070c
Revises: e79951599d68
Create Date: 2026-07-13 06:16:30.918554

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "87af8e11070c"
down_revision: Union[str, Sequence[str], None] = "e79951599d68"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("users", sa.Column("is_admin", sa.Boolean(), nullable=False, server_default=sa.text("false")))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("users", "is_admin")
