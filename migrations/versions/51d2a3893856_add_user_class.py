"""Add user class

Revision ID: 51d2a3893856
Revises: ad740d3bf59b
Create Date: 2020-04-13 14:27:51.861436

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '51d2a3893856'
down_revision = 'ad740d3bf59b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=100), nullable=True),
    sa.Column('password', sa.String(length=100), nullable=True),
    sa.Column('first_name', sa.String(length=1000), nullable=True),
    sa.Column('last_name', sa.String(length=1000), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user')
    # ### end Alembic commands ###