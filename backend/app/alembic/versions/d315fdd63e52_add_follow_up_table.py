"""add follow up table

Revision ID: d315fdd63e52
Revises: 73c6dadc5084
Create Date: 2024-04-20 09:49:19.511964

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = 'd315fdd63e52'
down_revision: Union[str, None] = '73c6dadc5084'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('follow_up',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('lead_id', sa.Integer(), nullable=True),
    sa.Column('leadStatus', sa.String(length=200), nullable=True),
    sa.Column('lead_status_id', sa.Integer(), nullable=True),
    sa.Column('createdBy', sa.Integer(), nullable=True),
    sa.Column('comment', sa.Text(), nullable=True),
    sa.Column('followup_dt', sa.DateTime(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('followup_status', mysql.TINYINT(), nullable=True, comment=' 1->follow_up,2-completeed-1->cancelled'),
    sa.Column('status', mysql.TINYINT(), nullable=True, comment=' 1->active,-1->deleted'),
    sa.ForeignKeyConstraint(['createdBy'], ['user.id'], ),
    sa.ForeignKeyConstraint(['lead_id'], ['lead.id'], ),
    sa.ForeignKeyConstraint(['lead_status_id'], ['lead_status.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('country', sa.Column('image', sa.String(length=255), nullable=True))
    op.alter_column('country', 'country_code',
               existing_type=mysql.VARCHAR(length=10),
               comment=None,
               existing_comment='phone code',
               existing_nullable=True)
    op.alter_column('country', 'sms_enabled',
               existing_type=mysql.TINYINT(display_width=1),
               nullable=True,
               comment='1->active,-1->deleted',
               existing_server_default=sa.text("'0'"))
    op.alter_column('country', 'status',
               existing_type=mysql.TINYINT(display_width=1),
               nullable=True,
               comment='1->active,-1->deleted',
               existing_comment='0->Inactive, 1->Active',
               existing_server_default=sa.text("'1'"))
    op.drop_table_comment(
        'country',
        existing_comment='Country master table',
        schema=None
    )
    op.drop_column('country', 'img')
    op.drop_column('lead', 'country_code')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('lead', sa.Column('country_code', mysql.VARCHAR(length=10), nullable=True))
    op.add_column('country', sa.Column('img', mysql.VARCHAR(length=255), nullable=True, comment='flag images or any icon images'))
    op.create_table_comment(
        'country',
        'Country master table',
        existing_comment=None,
        schema=None
    )
    op.alter_column('country', 'status',
               existing_type=mysql.TINYINT(display_width=1),
               nullable=False,
               comment='0->Inactive, 1->Active',
               existing_comment='1->active,-1->deleted',
               existing_server_default=sa.text("'1'"))
    op.alter_column('country', 'sms_enabled',
               existing_type=mysql.TINYINT(display_width=1),
               nullable=False,
               comment=None,
               existing_comment='1->active,-1->deleted',
               existing_server_default=sa.text("'0'"))
    op.alter_column('country', 'country_code',
               existing_type=mysql.VARCHAR(length=10),
               comment='phone code',
               existing_nullable=True)
    op.drop_column('country', 'image')
    op.drop_table('follow_up')
    # ### end Alembic commands ###