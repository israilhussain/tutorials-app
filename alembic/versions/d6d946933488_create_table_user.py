"""create table user

Revision ID: d6d946933488
Revises: fee2ce3afe8d
Create Date: 2025-01-09 19:23:28.657624

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd6d946933488'
down_revision: Union[str, None] = 'fee2ce3afe8d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table("users",
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('email', sa.VARCHAR(), nullable=False),
    sa.Column('password', sa.VARCHAR(), nullable=False),
    sa.PrimaryKeyConstraint('id') 
    )


def downgrade() -> None:
    op.drop_table('users')
