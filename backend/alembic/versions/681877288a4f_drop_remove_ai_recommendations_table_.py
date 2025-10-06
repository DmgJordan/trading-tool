"""drop: Remove ai_recommendations table (moved to future recommendations domain)

Revision ID: 681877288a4f
Revises: 730c2c573f71
Create Date: 2025-10-06 23:36:58.578851

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '681877288a4f'
down_revision: Union[str, Sequence[str], None] = '730c2c573f71'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Drop ai_recommendations table."""
    # Drop indexes first
    op.drop_index('idx_action_created', table_name='ai_recommendations')
    op.drop_index('idx_user_symbol', table_name='ai_recommendations')
    op.drop_index('idx_symbol_created', table_name='ai_recommendations')
    op.drop_index('idx_user_created', table_name='ai_recommendations')

    # Drop table
    op.drop_table('ai_recommendations')


def downgrade() -> None:
    """Downgrade schema - Recreate ai_recommendations table."""
    op.create_table(
        'ai_recommendations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('action', sa.String(length=10), nullable=False),
        sa.Column('symbol', sa.String(length=50), nullable=False),
        sa.Column('confidence', sa.Integer(), nullable=False),
        sa.Column('size_percentage', sa.Float(), nullable=False),
        sa.Column('entry_price', sa.Float(), nullable=True),
        sa.Column('stop_loss', sa.Float(), nullable=True),
        sa.Column('take_profit1', sa.Float(), nullable=True),
        sa.Column('take_profit2', sa.Float(), nullable=True),
        sa.Column('take_profit3', sa.Float(), nullable=True),
        sa.Column('reasoning', sa.Text(), nullable=True),
        sa.Column('risk_level', sa.String(length=10), nullable=False),
        sa.Column('market_data_timestamp', sa.DateTime(timezone=True), nullable=True),
        sa.Column('prompt_hash', sa.String(length=64), nullable=True),
        sa.Column('model_used', sa.String(length=100), nullable=True),
        sa.Column('actual_outcome', sa.String(length=50), nullable=True),
        sa.Column('actual_return', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Recreate indexes
    op.create_index('idx_user_created', 'ai_recommendations', ['user_id', 'created_at'])
    op.create_index('idx_symbol_created', 'ai_recommendations', ['symbol', 'created_at'])
    op.create_index('idx_user_symbol', 'ai_recommendations', ['user_id', 'symbol'])
    op.create_index('idx_action_created', 'ai_recommendations', ['action', 'created_at'])
    op.create_index(op.f('ix_ai_recommendations_id'), 'ai_recommendations', ['id'], unique=False)
    op.create_index(op.f('ix_ai_recommendations_symbol'), 'ai_recommendations', ['symbol'], unique=False)
    op.create_index(op.f('ix_ai_recommendations_user_id'), 'ai_recommendations', ['user_id'], unique=False)
