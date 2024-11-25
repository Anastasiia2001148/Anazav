"""description

Revision ID: 6c6f547369e6
Revises: 2d701ec4ffe0
Create Date: 2024-11-24 16:35:11.336010

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6c6f547369e6'
down_revision: Union[str, None] = '2d701ec4ffe0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('contapp', sa.Column('description', sa.String(length=250), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('contapp', 'description')
    # ### end Alembic commands ###
