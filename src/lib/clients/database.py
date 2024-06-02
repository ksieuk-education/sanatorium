"""Клиенты для работы с базами данных"""

import logging

import sqlalchemy
import sqlalchemy.ext.asyncio as sa_asyncio
import sqlalchemy.orm

import lib.app.split_settings as _app_split_settings

logger = logging.getLogger(__name__)


class AsyncDatabaseClient:
    """
    Асинхронный клиент базы данных, обеспечивающий создание асинхронных сессий для взаимодействия с базой данных.
    """

    def __init__(self, settings: _app_split_settings.DatabaseSettings) -> None:
        """
        Инициализирует асинхронный клиент базы данных с конфигурацией, полученной из настроек.

        :param settings: Экземпляр настроек базы данных, содержащий параметры подключения и пула.
        """

        self.settings = settings

        self.async_engine = sa_asyncio.create_async_engine(
            url=self.settings.dsn,
            pool_size=self.settings.pool_size,
            pool_pre_ping=self.settings.pool_pre_ping,
            echo=self.settings.echo,
            poolclass=sqlalchemy.pool.AsyncAdaptedQueuePool,
            future=True,
            connect_args={
                "statement_cache_size": 0,
                "prepared_statement_cache_size": 0,
            },
        )

    def get_sync_session(
        self,
    ) -> sqlalchemy.orm.sessionmaker[sqlalchemy.orm.Session]:  # pylint: disable=unsubscriptable-object]
        """
        Возвращает sessionmaker для синхронных сессий, что не поддерживается в асинхронном клиенте базы данных.

        :raise RuntimeError: Синхронные сессии не реализованы в AsyncDatabaseClient.
        """

        msg = "Sync session not implemented for AsyncDatabaseClient"
        raise RuntimeError(msg)

    def get_async_session(
        self,
    ) -> sa_asyncio.async_sessionmaker[sa_asyncio.AsyncSession]:
        """
        Создает и возвращает асинхронный sessionmaker, связанный c асинхронным движком базы данных.

        :return: Экземпляр async_sessionmaker для создания асинхронных сессий.
        """

        return sa_asyncio.async_sessionmaker(
            bind=self.async_engine,
            autocommit=self.settings.auto_commit,
            autoflush=self.settings.auto_flush,
            expire_on_commit=self.settings.expire_on_commit,
        )

    async def dispose_callback(self) -> None:
        """
        Асинхронно освобождает ресурсы, связанные c асинхронным движком базы данных.
        """

        await self.async_engine.dispose()
