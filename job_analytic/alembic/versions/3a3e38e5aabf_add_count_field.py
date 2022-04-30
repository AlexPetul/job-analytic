"""add count field

Revision ID: 3a3e38e5aabf
Revises: 857af15c732c
Create Date: 2022-03-11 22:25:05.189882

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3a3e38e5aabf'
down_revision = '857af15c732c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('position_skill', sa.Column('count', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('position_skill', 'count')
    # ### end Alembic commands ###