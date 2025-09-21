"""merge hyperliquid public address and ai recommendations branches

Revision ID: 730c2c573f71
Revises: 2b9644402df0, 4efaeb8afe04
Create Date: 2025-09-21 21:22:59.601151

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '730c2c573f71'
down_revision: Union[str, Sequence[str], None] = ('2b9644402df0', '4efaeb8afe04')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
