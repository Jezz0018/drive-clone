"""add_category_and_archive

Revision ID: 8e7cbd454794
Revises: 1ed3d74cca4a
Create Date: 2026-05-16 09:41:27.275930

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8e7cbd454794'
down_revision: Union[str, Sequence[str], None] = '1ed3d74cca4a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('items', sa.Column('is_archived', sa.Boolean(), nullable=True))
    op.execute("UPDATE items SET is_archived = false WHERE is_archived IS NULL")
    op.alter_column('items', 'is_archived', nullable=False, server_default=sa.text('false'))
    op.add_column('items', sa.Column('category', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('items', 'category')
    op.drop_column('items', 'is_archived')
