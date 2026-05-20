"""add profile picture field

Revision ID: 68489248294e
Revises: 865d29ff4342
Create Date: 2026-05-18 10:13:49.610892

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '68489248294e'
down_revision: Union[str, Sequence[str], None] = '865d29ff4342'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('users', sa.Column('profile_picture', sa.String(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'profile_picture')
