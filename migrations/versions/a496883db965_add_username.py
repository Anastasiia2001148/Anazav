"""add username

Revision ID: a496883db965
Revises: 33d730db7171
Create Date: 2024-11-13 16:00:20.137725

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a496883db965'
down_revision: Union[str, None] = '33d730db7171'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


"""add username

Revision ID: a496883db965
Revises: 33d730db7171
Create Date: 2024-11-13 16:00:20.137725

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a496883db965'
down_revision: Union[str, None] = '33d730db7171'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Добавляем новый столбец
    op.add_column('users', sa.Column('username', sa.String(), nullable=True))

    # Обновляем пустые значения
    op.execute("UPDATE users SET username = email WHERE username IS NULL")

    # Делаем столбец обязательным
    op.alter_column('users', 'username', nullable=False)

    # Создаем уникальный индекс
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)


def downgrade() -> None:
    # Удаляем индекс
    op.drop_index(op.f('ix_users_username'), table_name='users')

    # Удаляем столбец
    op.drop_column('users', 'username')