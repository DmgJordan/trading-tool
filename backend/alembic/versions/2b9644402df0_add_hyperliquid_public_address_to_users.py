"""add hyperliquid public address to users

Revision ID: 2b9644402df0
Revises: 570f414a545d
Create Date: 2025-09-21 21:13:24.121224

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2b9644402df0'
down_revision: Union[str, Sequence[str], None] = '570f414a545d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('users', sa.Column('hyperliquid_public_address', sa.String(length=66), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'hyperliquid_public_address')
