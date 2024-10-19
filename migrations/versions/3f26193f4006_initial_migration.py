"""Initial migration

Revision ID: 3f26193f4006
Revises: 
Create Date: 2024-10-19 12:55:25.102806

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3f26193f4006'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('api_key', schema=None) as batch_op:
        batch_op.add_column(sa.Column('design', sa.String(length=10), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('api_key', schema=None) as batch_op:
        batch_op.drop_column('design')

    # ### end Alembic commands ###
