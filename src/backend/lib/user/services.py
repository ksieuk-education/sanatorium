"""Сервисы для работы с пользователями"""

import uuid

import lib.app.errors as _app_errors
import lib.models as _models
import lib.models.orm as _models_orm
import lib.user.models as _user_models


class UserService:
    """Сервис для работы с пользователями"""

    def __init__(self, user_repository: _user_models.UserRepositoryProtocol) -> None:
        """
        Конструктор сервиса для работы с пользователями

        :param user_repository: Репозиторий для работы с пользователями
        """

        self._user_repository = user_repository

    async def create(self, request: _models.UserInfoModel) -> _models.UserFullModel:
        """
        Создание пользователя

        :param request: Модель пользователя для создания
        :return: Модель пользователя
        """

        user_orm_model = await self._user_repository.create(_models_orm.User(**request.model_dump()))
        return _models.UserFullModel.model_validate(user_orm_model.as_dict())

    async def get_by_id(self, user_id: uuid.UUID) -> _models.UserFullModel:
        """
        Получение пользователя по идентификатору

        :param user_id: Идентификатор пользователя
        :return: Модель пользователя
        """

        user_orm_model = await self._user_repository.get_by_id(user_id)
        if user_orm_model is None:
            msg = f"User with id {user_id} not found"
            raise _app_errors.RepositoryORMNotFoundError(msg)
        return _models.UserFullModel.model_validate(user_orm_model.as_dict())

    async def update(self, request: _models.UserOptionalModel) -> _models.UserFullModel:
        """
        Обновление пользователя

        :param request: Модель пользователя для обновления
        :return: Модель пользователя
        """

        user_orm_model = await self._user_repository.update(_models_orm.User(**request.model_dump()))
        return _models.UserFullModel.model_validate(user_orm_model.as_dict())

    async def delete(self, user_id: uuid.UUID) -> None:
        """
        Удаление пользователя

        :param user_id: Идентификатор пользователя
        """

        await self._user_repository.delete(user_id)
