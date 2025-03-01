"""empty message

Revision ID: 33564d15b8b1
Revises: c283ca4f8416
Create Date: 2025-02-25 22:01:23.567075

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '33564d15b8b1'
down_revision = 'c283ca4f8416'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('schools', schema=None) as batch_op:
        batch_op.add_column(sa.Column('principal_name', sa.String(length=100), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('schools', schema=None) as batch_op:
        batch_op.drop_column('principal_name')

    # ### end Alembic commands ###
