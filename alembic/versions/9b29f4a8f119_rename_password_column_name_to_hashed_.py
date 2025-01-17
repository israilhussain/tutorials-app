"""rename password column name to hashed_password

Revision ID: 9b29f4a8f119
Revises: d6d946933488
Create Date: 2025-01-09 20:14:33.127762

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9b29f4a8f119'
down_revision: Union[str, None] = 'd6d946933488'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('users', column_name="password", new_column_name="hashed_password")


def downgrade() -> None:
    pass
