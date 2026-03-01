"""Create subscription tables

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create subscription_tier enum
    subscription_tier_enum = postgresql.ENUM('free', 'premium', name='subscriptiontier', create_type=True)
    subscription_tier_enum.create(op.get_bind(), checkfirst=True)
    
    # Create subscription_status enum
    subscription_status_enum = postgresql.ENUM(
        'active', 'canceled', 'past_due', 'trialing', 'incomplete', 'incomplete_expired',
        name='subscriptionstatus', create_type=True
    )
    subscription_status_enum.create(op.get_bind(), checkfirst=True)
    
    # Create subscriptions table
    op.create_table(
        'subscriptions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('tier', subscription_tier_enum, nullable=False, server_default='free'),
        sa.Column('status', subscription_status_enum, nullable=False, server_default='active'),
        sa.Column('stripe_customer_id', sa.String(255), nullable=True),
        sa.Column('stripe_subscription_id', sa.String(255), nullable=True),
        sa.Column('stripe_price_id', sa.String(255), nullable=True),
        sa.Column('current_period_start', sa.DateTime(), nullable=True),
        sa.Column('current_period_end', sa.DateTime(), nullable=True),
        sa.Column('cancel_at_period_end', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('canceled_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_subscriptions_id', 'subscriptions', ['id'])
    op.create_index('ix_subscriptions_user_id', 'subscriptions', ['user_id'], unique=True)
    op.create_index('ix_subscriptions_stripe_customer_id', 'subscriptions', ['stripe_customer_id'], unique=True)
    op.create_index('ix_subscriptions_stripe_subscription_id', 'subscriptions', ['stripe_subscription_id'], unique=True)
    
    # Create subscription_usage table
    op.create_table(
        'subscription_usage',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('subscription_id', sa.Integer(), nullable=False),
        sa.Column('games_played_today', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('games_played_this_month', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_game_played_at', sa.DateTime(), nullable=True),
        sa.Column('daily_reset_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('monthly_reset_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['subscription_id'], ['subscriptions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_subscription_usage_id', 'subscription_usage', ['id'])
    op.create_index('ix_subscription_usage_subscription_id', 'subscription_usage', ['subscription_id'], unique=True)


def downgrade():
    op.drop_index('ix_subscription_usage_subscription_id', table_name='subscription_usage')
    op.drop_index('ix_subscription_usage_id', table_name='subscription_usage')
    op.drop_table('subscription_usage')
    
    op.drop_index('ix_subscriptions_stripe_subscription_id', table_name='subscriptions')
    op.drop_index('ix_subscriptions_stripe_customer_id', table_name='subscriptions')
    op.drop_index('ix_subscriptions_user_id', table_name='subscriptions')
    op.drop_index('ix_subscriptions_id', table_name='subscriptions')
    op.drop_table('subscriptions')
    
    # Drop enums
    sa.Enum(name='subscriptionstatus').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='subscriptiontier').drop(op.get_bind(), checkfirst=True)