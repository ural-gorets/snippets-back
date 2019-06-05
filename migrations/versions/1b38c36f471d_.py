"""empty message

Revision ID: 1b38c36f471d
Revises: 
Create Date: 2019-05-21 22:32:07.451332

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1b38c36f471d'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('snippets',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=200), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('preview', sa.Text(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('files',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('snippets_id', sa.Integer(), nullable=False),
    sa.Column('filename', sa.String(), nullable=False),
    sa.Column('data', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['snippets_id'], ['snippets.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('forms',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('snippets_id', sa.Integer(), nullable=False),
    sa.Column('data', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['snippets_id'], ['snippets.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('refs',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('snippets_id', sa.Integer(), nullable=False),
    sa.Column('ref', sa.String(), nullable=False),
    sa.Column('data', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['snippets_id'], ['snippets.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('refs')
    op.drop_table('forms')
    op.drop_table('files')
    op.drop_table('snippets')
    # ### end Alembic commands ###