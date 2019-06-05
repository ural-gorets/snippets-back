"""empty message

Revision ID: f5c6d167f379
Revises: b91d33016dd0
Create Date: 2019-06-01 18:15:07.190448

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f5c6d167f379'
down_revision = 'b91d33016dd0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('files_snippets_id_fkey', 'files', type_='foreignkey')
    op.drop_column('files', 'snippets_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('files', sa.Column('snippets_id', sa.INTEGER(), autoincrement=False, nullable=False))
    op.create_foreign_key('files_snippets_id_fkey', 'files', 'snippets', ['snippets_id'], ['id'])
    # ### end Alembic commands ###