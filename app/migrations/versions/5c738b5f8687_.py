"""empty message

Revision ID: 5c738b5f8687
Revises: 9eca6b8eb073
Create Date: 2025-02-23 13:21:22.338567

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5c738b5f8687'
down_revision = '9eca6b8eb073'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('students', schema=None) as batch_op:
        batch_op.drop_constraint('uq_students_user_id', type_='unique')
        batch_op.drop_constraint('fk_students_user_id', type_='foreignkey')
        batch_op.drop_column('user_id')

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_constraint('uq_users_student_id', type_='unique')
        batch_op.drop_constraint('fk_users_student_id', type_='foreignkey')
        batch_op.create_foreign_key('fk_users_student_id', 'users', ['student_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_constraint('fk_users_student_id', type_='foreignkey')
        batch_op.create_foreign_key('fk_users_student_id', 'students', ['student_id'], ['id'])
        batch_op.create_unique_constraint('uq_users_student_id', ['student_id'])

    with op.batch_alter_table('students', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_id', sa.INTEGER(), nullable=True))
        batch_op.create_foreign_key('fk_students_user_id', 'users', ['user_id'], ['id'])
        batch_op.create_unique_constraint('uq_students_user_id', ['user_id'])

    # ### end Alembic commands ###
