"""Generic Alembic revision script.

Revision ID: d0e34b587fc7
Revises: 0001_initial
Create Date: 2025-09-14 21:44:52.006407

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'd0e34b587fc7'
down_revision: Union[str, None] = '0001_initial'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    pass


def downgrade() -> None:
    pass