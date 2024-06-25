"""is_followup in lead

Revision ID: 1ac102300dff
Revises: 0b8e7e655ca5
Create Date: 2024-04-20 14:29:16.846011

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '1ac102300dff'
down_revision: Union[str, None] = '0b8e7e655ca5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('lead', sa.Column('is_followup', mysql.TINYINT(), nullable=True, comment='1->active,-1->inactive'))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('lead', 'is_followup')
    # ### end Alembic commands ###
