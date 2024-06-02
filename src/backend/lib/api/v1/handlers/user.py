"""Хэндлер для работы с пользователями"""

import logging
import uuid

import fastapi

import lib.api.v1.schemas as _api_schemas
import lib.user.services as _user_services

logger = logging.getLogger(__name__)


class UserHandler:
    """Хэндлер для работы с пользователями"""

    def __init__(
        self,
        user_service: _user_services.UserService,
    ) -> None:
        """
        Конструктор хэндлера для работы с пользователями

        :param user_service: Сервис для работы с пользователями
        """

        self._user_service = user_service
        self.router = fastapi.APIRouter()

        self.register_routers()

    def register_routers(self) -> None:
        """Регистрация роутеров"""

        self.router.add_api_route(
            path="/",
            endpoint=self.create,
            methods=["POST"],
            summary="Создание пользователя",
            description="Создает пользователя",
            status_code=fastapi.status.HTTP_200_OK,
        )
        self.router.add_api_route(
            path="/{user_id}",
            endpoint=self.get_by_id,
            methods=["GET"],
            summary="Получение пользователя по идентификатору",
            description="Получает пользователя по идентификатору",
            status_code=fastapi.status.HTTP_200_OK,
        )
        self.router.add_api_route(
            path="/",
            endpoint=self.update,
            methods=["PUT"],
            summary="Обновление пользователя",
            description="Обновляет пользователя",
            status_code=fastapi.status.HTTP_200_OK,
        )
        self.router.add_api_route(
            path="/{user_id}",
            endpoint=self.delete,
            methods=["DELETE"],
            summary="Удаление пользователя",
            description="Удаляет пользователя",
            status_code=fastapi.status.HTTP_200_OK,
        )

    async def create(self, request: _api_schemas.UserCreateSchema) -> _api_schemas.UserFullSchema:
        user_created = await self._user_service.create(request)
        return _api_schemas.UserFullSchema(**user_created.model_dump())

    async def get_by_id(self, user_id: uuid.UUID) -> _api_schemas.UserFullSchema | None:
        user = await self._user_service.get_by_id(user_id)
        return _api_schemas.UserFullSchema(**user.model_dump())

    async def update(self, request: _api_schemas.UserUpdateSchema) -> _api_schemas.UserFullSchema:
        user_updated = await self._user_service.update(request)
        return _api_schemas.UserFullSchema(**user_updated.model_dump())

    async def delete(self, user_id: uuid.UUID) -> None:
        await self._user_service.delete(user_id)
