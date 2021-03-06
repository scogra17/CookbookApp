"""add ownership fields to recipe table

Revision ID: 6302df848cdf
Revises: 51d2a3893856
Create Date: 2020-04-16 10:33:28.164890

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6302df848cdf'
down_revision = '51d2a3893856'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('recipe', sa.Column('created_by', sa.String(length=100), nullable=True))
    op.add_column('recipe', sa.Column('is_public', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('recipe', 'is_public')
    op.drop_column('recipe', 'created_by')
    # ### end Alembic commands ###
