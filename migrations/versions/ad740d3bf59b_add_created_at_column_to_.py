"""Add created_at column to RecipeIngredient model

Revision ID: ad740d3bf59b
Revises: 6ba041274881
Create Date: 2020-04-03 12:40:42.648890

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ad740d3bf59b'
down_revision = '6ba041274881'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('recipe_ingredient', sa.Column('created_at', sa.DateTime()))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('recipe_ingredient', 'created_at')
    # ### end Alembic commands ###
