"""add_user_trading_preferences_table

Revision ID: e2d856a6d829
Revises: 378e6f7191fe
Create Date: 2025-09-16 21:58:01.138898

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'e2d856a6d829'
down_revision: Union[str, Sequence[str], None] = '378e6f7191fe'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create user_trading_preferences table
    op.create_table(
        'user_trading_preferences',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('risk_tolerance', sa.Enum('LOW', 'MEDIUM', 'HIGH', name='risktolerance'), nullable=False),
        sa.Column('investment_horizon', sa.Enum('SHORT_TERM', 'MEDIUM_TERM', 'LONG_TERM', name='investmenthorizon'), nullable=False),
        sa.Column('trading_style', sa.Enum('CONSERVATIVE', 'BALANCED', 'AGGRESSIVE', name='tradingstyle'), nullable=False),
        sa.Column('max_position_size', sa.Float(), nullable=False),
        sa.Column('stop_loss_percentage', sa.Float(), nullable=False),
        sa.Column('take_profit_ratio', sa.Float(), nullable=False),
        sa.Column('preferred_assets', sa.Text(), nullable=True),
        sa.Column('technical_indicators', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint('max_position_size > 0 AND max_position_size <= 100', name='check_max_position_size_range'),
        sa.CheckConstraint('stop_loss_percentage > 0 AND stop_loss_percentage <= 50', name='check_stop_loss_percentage_range'),
        sa.CheckConstraint('take_profit_ratio > 0 AND take_profit_ratio <= 10', name='check_take_profit_ratio_range'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )

    # Create indexes
    op.create_index(op.f('ix_user_trading_preferences_id'), 'user_trading_preferences', ['id'], unique=False)
    op.create_index(op.f('ix_user_trading_preferences_user_id'), 'user_trading_preferences', ['user_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Drop indexes
    op.drop_index(op.f('ix_user_trading_preferences_user_id'), table_name='user_trading_preferences')
    op.drop_index(op.f('ix_user_trading_preferences_id'), table_name='user_trading_preferences')

    # Drop user_trading_preferences table
    op.drop_table('user_trading_preferences')

    # Drop enum types
    op.execute('DROP TYPE IF EXISTS risktolerance')
    op.execute('DROP TYPE IF EXISTS investmenthorizon')
    op.execute('DROP TYPE IF EXISTS tradingstyle')
