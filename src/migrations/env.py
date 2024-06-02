"""
Функции для выполнения миграций схемы базы данных

Этот модуль предоставляет функции для настройки и выполнения миграций,
 основываясь на состоянии схемы базы данных и таблиц.
"""

import asyncio
from logging.config import fileConfig

import sqlalchemy.schema as sa_schema
from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

import lib.app.settings as _settings
import lib.models.orm as _models_orm

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

SCHEMA_NAME = "content"
config.set_main_option("sqlalchemy.url", _settings.Settings().database.dsn)

target_metadata = _models_orm.Base.metadata


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.
    """

    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        version_table_schema=SCHEMA_NAME,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """
    Выполняет миграции базы данных

    Использует соединение с базой данных для запуска миграций с использованием Alembic.
    Конфигурирует контекст миграции для включения схем и таблиц определенной схемы.

    :param connection: Соединение с базой данных, через которое будут выполняться миграции
    :return: None
    """

    # pylint: disable-next=unused-argument
    def include_name(
        name: str | None,
        type_: str,
        parent_names: dict[str, str] | None,  # noqa: ARG001  # pylint: disable=unused-argument
    ) -> bool:
        """
        Определяет, следует ли включать объект схемы в миграцию по имени

        Переопределяет https://alembic.sqlalchemy.org/en/latest/api/runtime.html#alembic.runtime.environment.EnvironmentContext.configure.params.include_name

        :param name: Имя объекта
        :param type_: Тип объекта, например 'schema'
        :param parent_names: Словарь родительских имен
        :return: Возвращает True, если схема должна быть включена в миграцию, иначе False
        """

        if type_ == "schema":
            return name in (SCHEMA_NAME,)
        return True

    def include_object(
        object_: sa_schema.SchemaItem | sa_schema.Table,
        name: str,  # noqa: ARG001  # pylint: disable=unused-argument
        type_: str,
        reflected: bool,  # noqa: ARG001, FBT001  # pylint: disable=unused-argument
        compare_to: sa_schema.SchemaItem | sa_schema.Table | None,  # noqa: ARG001 # pylint: disable=unused-argument
    ) -> bool:
        """
        Определяет, следует ли включать объект базы данных в миграцию

        Переопределяет https://alembic.sqlalchemy.org/en/latest/api/runtime.html#alembic.runtime.environment.EnvironmentContext.configure.params.include_object

        :param object_: Объект схемы, например таблица SQLAlchemy
        :param name: Имя объекта
        :param type_: Тип объекта, например 'table'
        :param reflected: Указывает, отражен ли объект
        :param compare_to: Объект, с которым сравнивается текущий объект
        :return: Возвращает True, если объект должен быть включен в миграцию, иначе False
        """

        if type_ == "table" and isinstance(object_, sa_schema.Table):
            return object_.schema in (SCHEMA_NAME,)
        return True

    context.configure(
        include_schemas=True,
        include_name=include_name,  # type: ignore[reportUnknownParameterType]
        include_object=include_object,  # type: ignore[reportUnknownParameterType]
        connection=connection,
        target_metadata=target_metadata,
        version_table_schema=SCHEMA_NAME,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine and associate a connection with the context"""

    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        connect_args={"statement_cache_size": 0},
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode"""

    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
