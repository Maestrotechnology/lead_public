"""your_revision_message

Revision ID: 6b603f0c0e43
Revises: f3766ae8a8b5
Create Date: 2024-02-23 11:37:16.420397

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6b603f0c0e43'
down_revision: Union[str, None] = 'f3766ae8a8b5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###