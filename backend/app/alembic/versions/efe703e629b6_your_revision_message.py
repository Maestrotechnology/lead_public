"""your_revision_message

Revision ID: efe703e629b6
Revises: 6b603f0c0e43
Create Date: 2024-02-23 11:38:25.231293

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'efe703e629b6'
down_revision: Union[str, None] = '6b603f0c0e43'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('lead', sa.Column('states', sa.String(length=50), nullable=True))
    op.add_column('user', sa.Column('states', sa.String(length=50), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'states')
    op.drop_column('lead', 'states')
    # ### end Alembic commands ###
