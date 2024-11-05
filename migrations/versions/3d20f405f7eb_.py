"""empty message

Revision ID: 3d20f405f7eb
Revises: 05bacf889072
Create Date: 2024-11-04 12:11:46.996787

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3d20f405f7eb'
down_revision = '05bacf889072'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('task', schema=None) as batch_op:
        batch_op.add_column(sa.Column('goal_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(None, 'goal', ['goal_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('task', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('goal_id')

    # ### end Alembic commands ###