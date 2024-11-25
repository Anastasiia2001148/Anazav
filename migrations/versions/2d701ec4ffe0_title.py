"""title

Revision ID: 2d701ec4ffe0
Revises: a581a28a1d7b
Create Date: 2024-11-24 16:33:46.814296

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2d701ec4ffe0'
down_revision: Union[str, None] = 'a581a28a1d7b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('contapp', sa.Column('title', sa.String(length=50), nullable=True))
    op.create_index(op.f('ix_contapp_title'), 'contapp', ['title'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_contapp_title'), table_name='contapp')
    op.drop_column('contapp', 'title')
    # ### end Alembic commands ###
