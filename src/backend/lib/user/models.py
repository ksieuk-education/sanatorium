"""Модели для работы с пользователями"""

import typing
import uuid

import lib.models.orm as _models_orm


class UserRepositoryProtocol(typing.Protocol):
    """Интерфейс для работы с репозиторием пользователей"""

    async def create(self, item: _models_orm.User) -> _models_orm.User:
        """
        Создание пользователя

        :param item: Модель пользователя для создания
        :return: Модель пользователя
        """
        raise NotImplementedError

    async def get_by_id(self, item_id: uuid.UUID) -> _models_orm.User | None:
        """
        Получение пользователя по идентификатору

        :param item_id: Идентификатор пользователя
        :return: Модель пользователя
        """
        raise NotImplementedError

    async def update(self, item: _models_orm.User) -> _models_orm.User:
        """
        Обновление пользователя

        :param item: Модель пользователя для обновления
        :return: Модель пользователя
        """
        raise NotImplementedError

    async def delete(self, item_id: uuid.UUID) -> None:
        """
        Удаление пользователя

        :param item_id: Идентификатор пользователя
        """
        raise NotImplementedError
