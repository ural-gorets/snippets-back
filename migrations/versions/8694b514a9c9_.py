"""empty message

Revision ID: 8694b514a9c9
Revises: f5c6d167f379
Create Date: 2019-06-01 18:17:46.275594

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8694b514a9c9'
down_revision = 'f5c6d167f379'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('files', sa.Column('snippets_id', sa.Integer(), nullable=True))
    # op.create_foreign_key(None, 'files', 'snippets', ['snippets_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'files', type_='foreignkey')
    op.drop_column('files', 'snippets_id')
    # ### end Alembic commands ###
