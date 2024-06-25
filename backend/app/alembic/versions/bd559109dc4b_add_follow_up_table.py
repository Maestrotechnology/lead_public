"""add follow up table

Revision ID: bd559109dc4b
Revises: 48145d79d967
Create Date: 2024-04-20 10:27:18.600198

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bd559109dc4b'
down_revision: Union[str, None] = '48145d79d967'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('follow_up', sa.Column('updated_at', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('follow_up', 'updated_at')
    # ### end Alembic commands ###