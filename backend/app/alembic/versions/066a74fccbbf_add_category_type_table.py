"""add category_type table

Revision ID: 066a74fccbbf
Revises: 7af65445def1
Create Date: 2024-05-08 14:27:11.165481

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '066a74fccbbf'
down_revision: Union[str, None] = '7af65445def1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('lead', sa.Column('poc_date', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('lead', 'poc_date')
    # ### end Alembic commands ###