"""add missing order fields

Revision ID: 0006_add_missing_order_fields
Revises: 0005_product_columns
Create Date: 2026-01-16 11:15:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import sqlmodel

# revision identifiers, used by Alembic.
revision = '0006_add_missing_order_fields'
down_revision = '0005_product_columns'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add missing columns to order table
    op.add_column('order', sa.Column('shipping_fee', sa.Numeric(precision=10, scale=2), server_default='0.00', nullable=False))
    op.add_column('order', sa.Column('tax_amount', sa.Numeric(precision=10, scale=2), server_default='0.00', nullable=False))
    op.add_column('order', sa.Column('shipping_address', postgresql.JSON(astext_type=sa.Text()), nullable=True))
    op.add_column('order', sa.Column('tracking_number', sqlmodel.sql.sqltypes.AutoString(length=100), nullable=True))
    op.add_column('order', sa.Column('notes', sqlmodel.sql.sqltypes.AutoString(length=1000), nullable=True))
    op.add_column('order', sa.Column('estimated_delivery_date', sa.DateTime(), nullable=True))
    op.add_column('order', sa.Column('delivered_at', sa.DateTime(), nullable=True))
    op.add_column('order', sa.Column('cancelled_at', sa.DateTime(), nullable=True))
    op.add_column('order', sa.Column('cancellation_reason', sqlmodel.sql.sqltypes.AutoString(length=500), nullable=True))
    op.add_column('order', sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False))


def downgrade() -> None:
    op.drop_column('order', 'updated_at')
    op.drop_column('order', 'cancellation_reason')
    op.drop_column('order', 'cancelled_at')
    op.drop_column('order', 'delivered_at')
    op.drop_column('order', 'estimated_delivery_date')
    op.drop_column('order', 'stripe_payment_intent_id')
    op.drop_column('order', 'stripe_checkout_session_id')
    op.drop_column('order', 'notes')
    op.drop_column('order', 'tracking_number')
    op.drop_column('order', 'shipping_address')
    op.drop_column('order', 'tax_amount')
    op.drop_column('order', 'shipping_fee')
