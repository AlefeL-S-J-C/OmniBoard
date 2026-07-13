"""initial migration

Revision ID: 001
Revises: 
Create Date: 2026-07-13

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('password_hash', sa.String(length=255), nullable=True),
        sa.Column('provider', sa.String(length=20), nullable=True),
        sa.Column('provider_id', sa.String(length=100), nullable=True),
        sa.Column('fcm_token', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True, nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username'),
        sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # Create matches table
    op.create_table(
        'matches',
        sa.Column('id', sa.String(length=64), nullable=False),
        sa.Column('game_type', sa.String(length=50), nullable=False),
        sa.Column('player_white', sa.String(length=100), nullable=True),
        sa.Column('player_black', sa.String(length=100), nullable=True),
        sa.Column('player_white_id', sa.Integer(), nullable=True),
        sa.Column('player_black_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), onupdate=sa.text('now()'), nullable=True),
        sa.Column('status', sa.String(length=20), default='in_progress', nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Create match_events table
    op.create_table(
        'match_events',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('match_id', sa.String(length=64), nullable=False),
        sa.Column('turn', sa.Integer(), nullable=False),
        sa.Column('player', sa.String(length=50), nullable=False),
        sa.Column('action', sa.Text(), nullable=False),
        sa.Column('new_state', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['match_id'], ['matches.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_match_events_match_id'), 'match_events', ['match_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_match_events_match_id'), table_name='match_events')
    op.drop_table('match_events')
    op.drop_table('matches')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_table('users')