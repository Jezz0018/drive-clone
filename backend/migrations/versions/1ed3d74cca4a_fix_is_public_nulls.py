"""fix_is_public_nulls

Revision ID: 1ed3d74cca4a
Revises: c9f56f4cedb7
Create Date: 2026-05-16 09:35:50.472989

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1ed3d74cca4a'
down_revision: Union[str, Sequence[str], None] = 'c9f56f4cedb7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("UPDATE items SET is_public = false WHERE is_public IS NULL")
    op.alter_column('items', 'is_public', nullable=False, server_default=sa.text('false'))


def downgrade() -> None:
    op.alter_column('items', 'is_public', nullable=True, server_default=None)
