"""your_revision_message

Revision ID: 01f0713106f5
Revises: 89e0acdd9c7f
Create Date: 2024-02-23 16:39:51.548245

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '01f0713106f5'
down_revision: Union[str, None] = '89e0acdd9c7f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('lead_media', sa.Column('lead_history_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'lead_media', 'lead_history', ['lead_history_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'lead_media', type_='foreignkey')
    op.drop_column('lead_media', 'lead_history_id')
    # ### end Alembic commands ###
