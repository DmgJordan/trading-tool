"""add_ai_recommendations_table

Revision ID: 4efaeb8afe04
Revises: e2d856a6d829
Create Date: 2025-09-16 22:36:02.803756

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '4efaeb8afe04'
down_revision: Union[str, Sequence[str], None] = 'e2d856a6d829'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create ai_recommendations table without explicit enum creation
    # SQLAlchemy will handle enum creation automatically with checkfirst=True
    op.create_table(
        'ai_recommendations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('action', sa.String(length=10), nullable=False),  # Use String instead of Enum for now
        sa.Column('symbol', sa.String(length=50), nullable=False),
        sa.Column('confidence', sa.Integer(), nullable=False),
        sa.Column('size_percentage', sa.Float(), nullable=False),
        sa.Column('entry_price', sa.Float(), nullable=True),
        sa.Column('stop_loss', sa.Float(), nullable=True),
        sa.Column('take_profit1', sa.Float(), nullable=True),
        sa.Column('take_profit2', sa.Float(), nullable=True),
        sa.Column('take_profit3', sa.Float(), nullable=True),
        sa.Column('reasoning', sa.Text(), nullable=True),
        sa.Column('risk_level', sa.String(length=10), nullable=False),  # Use String instead of Enum for now
        sa.Column('market_data_timestamp', sa.DateTime(timezone=True), nullable=True),
        sa.Column('prompt_hash', sa.String(length=64), nullable=True),
        sa.Column('model_used', sa.String(length=100), nullable=True),
        sa.Column('actual_outcome', sa.String(length=50), nullable=True),
        sa.Column('actual_return', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        # Add constraints to validate enum values
        sa.CheckConstraint("action IN ('buy', 'sell', 'hold')", name='check_action_values'),
        sa.CheckConstraint("risk_level IN ('low', 'medium', 'high')", name='check_risk_level_values')
    )

    # Create indexes
    op.create_index(op.f('ix_ai_recommendations_id'), 'ai_recommendations', ['id'], unique=False)
    op.create_index(op.f('ix_ai_recommendations_user_id'), 'ai_recommendations', ['user_id'], unique=False)
    op.create_index(op.f('ix_ai_recommendations_symbol'), 'ai_recommendations', ['symbol'], unique=False)
    op.create_index('idx_user_created', 'ai_recommendations', ['user_id', 'created_at'], unique=False)
    op.create_index('idx_symbol_created', 'ai_recommendations', ['symbol', 'created_at'], unique=False)
    op.create_index('idx_user_symbol', 'ai_recommendations', ['user_id', 'symbol'], unique=False)
    op.create_index('idx_action_created', 'ai_recommendations', ['action', 'created_at'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Drop indexes
    op.drop_index('idx_action_created', table_name='ai_recommendations')
    op.drop_index('idx_user_symbol', table_name='ai_recommendations')
    op.drop_index('idx_symbol_created', table_name='ai_recommendations')
    op.drop_index('idx_user_created', table_name='ai_recommendations')
    op.drop_index(op.f('ix_ai_recommendations_symbol'), table_name='ai_recommendations')
    op.drop_index(op.f('ix_ai_recommendations_user_id'), table_name='ai_recommendations')
    op.drop_index(op.f('ix_ai_recommendations_id'), table_name='ai_recommendations')

    # Drop ai_recommendations table
    op.drop_table('ai_recommendations')
