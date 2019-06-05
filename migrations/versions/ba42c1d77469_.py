"""empty message

Revision ID: ba42c1d77469
Revises: 8b350ab206cb
Create Date: 2019-05-29 11:24:42.936082

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ba42c1d77469'
down_revision = '8b350ab206cb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('snippets', sa.Column('reference', sa.String(), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('snippets', 'reference')
    # ### end Alembic commands ###