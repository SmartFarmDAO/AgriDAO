"""add ecosystem roles

Revision ID: 0007_add_ecosystem_roles
Revises: 0006_add_missing_order_fields
Create Date: 2026-01-17 20:15:00.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel

# revision identifiers, used by Alembic.
revision = '0007_add_ecosystem_roles'
down_revision = '0006_add_missing_order_fields'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add sub_role column to user table
    op.add_column('user', sa.Column('sub_role', sqlmodel.sql.sqltypes.AutoString(length=100), nullable=True))


def downgrade() -> None:
    op.drop_column('user', 'sub_role')
