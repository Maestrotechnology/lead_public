"""add category_type table

Revision ID: 7af65445def1
Revises: c2e1b1aa8f98
Create Date: 2024-05-02 17:38:42.011871

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7af65445def1'
down_revision: Union[str, None] = 'c2e1b1aa8f98'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('lead', sa.Column('landline_number', sa.String(length=20), nullable=True))
    op.add_column('user', sa.Column('landline_number', sa.String(length=20), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'landline_number')
    op.drop_column('lead', 'landline_number')
    # ### end Alembic commands ###