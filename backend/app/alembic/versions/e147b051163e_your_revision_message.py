"""your_revision_message

Revision ID: e147b051163e
Revises: 01f0713106f5
Create Date: 2024-02-23 16:46:39.149362

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e147b051163e'
down_revision: Union[str, None] = '01f0713106f5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('lead_media', sa.Column('upload_by', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'lead_media', 'user', ['upload_by'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'lead_media', type_='foreignkey')
    op.drop_column('lead_media', 'upload_by')
    # ### end Alembic commands ###
