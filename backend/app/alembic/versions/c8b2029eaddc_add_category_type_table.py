"""add category_type table

Revision ID: c8b2029eaddc
Revises: 497395810e7c
Create Date: 2024-05-10 09:20:49.776697

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c8b2029eaddc'
down_revision: Union[str, None] = '497395810e7c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('lead_history', sa.Column('enquiry_type_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'lead_history', 'enquiry_type', ['enquiry_type_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'lead_history', type_='foreignkey')
    op.drop_column('lead_history', 'enquiry_type_id')
    # ### end Alembic commands ###
