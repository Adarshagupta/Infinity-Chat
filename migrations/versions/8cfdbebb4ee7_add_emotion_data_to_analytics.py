"""Add emotion_data to Analytics

Revision ID: 8cfdbebb4ee7
Revises: 62ed5c487ccc
Create Date: 2024-08-23 19:55:28.145855

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8cfdbebb4ee7'
down_revision = '62ed5c487ccc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('analytics', schema=None) as batch_op:
        batch_op.add_column(sa.Column('emotion_data', sa.Text(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('analytics', schema=None) as batch_op:
        batch_op.drop_column('emotion_data')

    # ### end Alembic commands ###