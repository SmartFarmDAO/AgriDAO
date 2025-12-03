"""add quantity_available to product

Revision ID: 0004_quantity_available
Revises: 0003_session_tables
Create Date: 2025-12-02

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0004_quantity_available'
down_revision = '0003_session_tables'
branch_labels = None
depends_on = None


def upgrade():
    # Add quantity_available column to product table
    op.add_column('product', sa.Column('quantity_available', sa.Integer(), nullable=False, server_default='0'))


def downgrade():
    op.drop_column('product', 'quantity_available')
