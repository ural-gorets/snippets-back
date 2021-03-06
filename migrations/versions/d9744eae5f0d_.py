"""empty message

Revision ID: d9744eae5f0d
Revises: 3f585079962c
Create Date: 2019-05-31 20:56:50.231561

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd9744eae5f0d'
down_revision = '3f585079962c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('files', sa.Column('type', sa.String(), nullable=True))
    op.create_unique_constraint(None, 'snippets', ['name'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'snippets', type_='unique')
    op.drop_column('files', 'type')
    # ### end Alembic commands ###
