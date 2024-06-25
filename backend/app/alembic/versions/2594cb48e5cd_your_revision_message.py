"""your_revision_message

Revision ID: 2594cb48e5cd
Revises: efe703e629b6
Create Date: 2024-02-23 12:01:46.498582

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '2594cb48e5cd'
down_revision: Union[str, None] = 'efe703e629b6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('lead', sa.Column('drop_reason', sa.Text(), nullable=True))
    op.drop_column('lead', 'cancel_reason')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('lead', sa.Column('cancel_reason', mysql.TEXT(), nullable=True))
    op.drop_column('lead', 'drop_reason')
    # ### end Alembic commands ###
