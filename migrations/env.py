import sys
from logging.config import fileConfig
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from alembic import context
from src.models import models # Замените на путь к вашей модели

# Этот файл содержит конфигурацию Alembic
config = context.config

# Настройка логирования
fileConfig(config.config_file_name)

# Устанавливаем URL соединения
sqlalchemy_url = config.get_main_option("sqlalchemy.url")
engine = create_engine(sqlalchemy_url)

# Объект с метаданными вашей модели
target_metadata = models.Base.metadata  # Замените на вашу метаданные

def run_migrations_online():
    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()

def run_migrations_offline():
    context.configure(
        url=sqlalchemy_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

# Запускаем миграции в зависимости от режима
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()


