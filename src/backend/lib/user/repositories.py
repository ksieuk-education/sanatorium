"""Репозиторий для работы с пользователями"""

import uuid

import sqlalchemy
import sqlalchemy.ext.asyncio as sa_asyncio

import lib.app.errors as _app_errors
import lib.models.orm as _models_orm


class UserRepository:
    """Репозиторий для работы с пользователями"""

    def __init__(self, async_session: sa_asyncio.async_sessionmaker[sa_asyncio.AsyncSession]) -> None:
        """
        Конструктор репозитория для работы с пользователями

        :param async_session: Асинхронный сеанс для работы с базой данных
        """

        self._async_session = async_session

    async def create(self, item: _models_orm.User) -> _models_orm.User:
        """
        Создание пользователя

        :param item: Модель пользователя для создания
        :return: Модель пользователя
        """

        async with self._async_session() as session, session.begin():
            session.add(item)
        return item

    async def get_by_id(self, item_id: uuid.UUID) -> _models_orm.User | None:
        """
        Получение пользователя по идентификатору

        :param item_id: Идентификатор пользователя
        :return: Модель пользователя
        """

        async with self._async_session() as session:
            return await session.get(_models_orm.User, item_id)

    async def update(self, item: _models_orm.User) -> _models_orm.User:
        """
        Обновление пользователя

        :param item: Модель пользователя для обновления
        :return: Модель пользователя
        """

        async with self._async_session() as session, session.begin():
            query = (
                sqlalchemy.update(_models_orm.User)
                .where(_models_orm.User.id == item.id)
                .values(**item.as_dict(exclude_none=True))
                .returning(_models_orm.User)
            )
            result = await session.execute(query)

        user_model = result.scalar()
        if user_model is None:
            msg = f"User with id: {item.id} not found"
            raise _app_errors.RepositoryORMNotFoundError(msg)
        return user_model

    async def delete(self, item_id: uuid.UUID) -> None:
        """
        Удаление пользователя

        :param item_id: Идентификатор пользователя
        """

        async with self._async_session() as session, session.begin():
            query = sqlalchemy.delete(_models_orm.User).where(_models_orm.User.id == item_id)
            result = await session.execute(query)
            if result.rowcount == 0:
                msg = f"User with id: {item_id} not found"
                raise _app_errors.RepositoryORMNotFoundError(msg)
