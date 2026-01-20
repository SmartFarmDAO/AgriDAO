"""add missing product columns

Revision ID: 0005_product_columns
Revises: 0004_quantity_available
Create Date: 2025-12-02

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0005_product_columns'
down_revision = '0004_quantity_available'
branch_labels = None
depends_on = None


def upgrade():
    # Add missing columns to product table
    op.add_column('product', sa.Column('unit', sa.String(length=50), nullable=False, server_default='piece'))
    op.add_column('product', sa.Column('status', sa.String(length=50), nullable=False, server_default='active'))
    op.add_column('product', sa.Column('images', postgresql.JSON(), nullable=True))
    op.add_column('product', sa.Column('product_metadata', postgresql.JSON(), nullable=True))
    op.add_column('product', sa.Column('sku', sa.String(length=100), nullable=True))
    op.add_column('product', sa.Column('weight', sa.Numeric(precision=8, scale=2), nullable=True))
    op.add_column('product', sa.Column('dimensions', postgresql.JSON(), nullable=True))
    op.add_column('product', sa.Column('tags', postgresql.JSON(), nullable=True))
    op.add_column('product', sa.Column('min_order_quantity', sa.Integer(), nullable=False, server_default='1'))
    op.add_column('product', sa.Column('max_order_quantity', sa.Integer(), nullable=True))
    op.add_column('product', sa.Column('harvest_date', sa.DateTime(), nullable=True))
    op.add_column('product', sa.Column('expiry_date', sa.DateTime(), nullable=True))
    op.add_column('product', sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')))
    
    # Add unique constraint on sku
    op.create_unique_constraint('uq_product_sku', 'product', ['sku'])


def downgrade():
    op.drop_constraint('uq_product_sku', 'product', type_='unique')
    op.drop_column('product', 'updated_at')
    op.drop_column('product', 'expiry_date')
    op.drop_column('product', 'harvest_date')
    op.drop_column('product', 'max_order_quantity')
    op.drop_column('product', 'min_order_quantity')
    op.drop_column('product', 'tags')
    op.drop_column('product', 'dimensions')
    op.drop_column('product', 'weight')
    op.drop_column('product', 'sku')
    op.drop_column('product', 'product_metadata')
    op.drop_column('product', 'images')
    op.drop_column('product', 'status')
    op.drop_column('product', 'unit')
