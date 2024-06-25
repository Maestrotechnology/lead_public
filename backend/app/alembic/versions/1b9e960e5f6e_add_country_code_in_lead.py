"""add country_code in lead

Revision ID: 1b9e960e5f6e
Revises: c3059a53ebd2
Create Date: 2024-04-17 14:12:01.952126

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1b9e960e5f6e'
down_revision: Union[str, None] = 'c3059a53ebd2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('country_code', sa.String(length=10), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'country_code')
    # ### end Alembic commands ###
