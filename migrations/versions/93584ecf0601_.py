"""empty message

Revision ID: 93584ecf0601
Revises: 3c6f7ddaf60d
Create Date: 2021-11-09 19:41:09.157659

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '93584ecf0601'
down_revision = '3c6f7ddaf60d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('rental', sa.Column('checkout_date', sa.DateTime(), server_default=sa.text('now()'), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('rental', 'checkout_date')
    # ### end Alembic commands ###
