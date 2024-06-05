"""Главное приложение"""

import dataclasses
import logging
import logging.config as logging_config
import typing

import fastapi
import pydantic
import sqladmin
import uvicorn

import lib.api.v1.handlers as _api_v1_handlers
import lib.app.errors as _app_errors
import lib.app.settings as _app_settings
import lib.app.split_settings as _app_split_settings
import lib.clients as _clients
import lib.models.admin_views as _models_admin_views
import lib.user.repositories as _user_repositories
import lib.user.services as _user_services

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class DisposableResource:
    name: str
    dispose_callback: typing.Awaitable[typing.Any]


class Application:
    """Приложение для запуска"""

    def __init__(
        self,
        settings: _app_settings.Settings,
        fastapi_app: fastapi.FastAPI,
        disposable_resources: list[DisposableResource],
    ) -> None:
        """
        Конструктор для создания приложения

        :param settings: Настройки проекта
        :param fastapi_app: Fastapi приложения
        :param disposable_resources: Ресурсы, которые нужно будет освободить после окончания работы приложения
        """

        self._settings = settings
        self._fastapi_app = fastapi_app
        self._disposable_resources = disposable_resources

    @classmethod
    def from_settings(cls, settings: _app_settings.Settings) -> "Application":
        """
        Создание приложения и инициализация всех клиентов, репозиториев, сервисов и хэндлеров из настроек

        :param settings: Настройки
        :return: Приложение
        """

        # Logging

        logging_config.dictConfig(_app_split_settings.get_logging_config(**settings.logger.model_dump()))

        logger.info("Initializing application")
        disposable_resources: list[DisposableResource] = []

        # Global clients
        logger.info("Initializing global clients")

        # Clients
        logger.info("Initializing clients")

        database_client = _clients.AsyncDatabaseClient(settings=settings.database)
        disposable_resources.append(
            DisposableResource(
                name="database_client",
                dispose_callback=database_client.dispose_callback(),
            )
        )

        # Repositories
        logger.info("Initializing repositories")

        user_repository = _user_repositories.UserRepository(async_session=database_client.get_async_session())

        # Caches
        logger.info("Initializing caches")

        # Services
        logger.info("Initializing services")

        user_service = _user_services.UserService(user_repository=user_repository)

        # Handlers
        logger.info("Initializing handlers")
        liveness_probe_handler = _api_v1_handlers.health_router
        user_handler = _api_v1_handlers.UserHandler(user_service=user_service)

        logger.info("Creating application")

        fastapi_app = fastapi.FastAPI(
            title=settings.app.title,
            version=settings.app.version,
            docs_url=settings.app.docs_url,
            openapi_url=settings.app.openapi_url,
            default_response_class=fastapi.responses.ORJSONResponse,
        )

        # Admin
        fastapi_admin = sqladmin.Admin(fastapi_app, database_client.async_engine)

        fastapi_admin.add_view(_models_admin_views.UserView)
        fastapi_admin.add_view(_models_admin_views.AdminView)
        fastapi_admin.add_view(_models_admin_views.RegistrationView)
        fastapi_admin.add_view(_models_admin_views.TravelPackageView)
        fastapi_admin.add_view(_models_admin_views.RoomView)
        fastapi_admin.add_view(_models_admin_views.DiningTableView)
        fastapi_admin.add_view(_models_admin_views.RoomTypeView)
        fastapi_admin.add_view(_models_admin_views.DiningTypeView)
        fastapi_admin.add_view(_models_admin_views.PhysicianView)

        # Routes
        fastapi_app.include_router(liveness_probe_handler, prefix="/api/v1/health", tags=["health"])
        fastapi_app.include_router(user_handler.router, prefix="/api/v1/users", tags=["user"])

        fastapi_app.add_exception_handler(pydantic.ValidationError, _api_v1_handlers.value_error_exception_handler)
        fastapi_app.add_exception_handler(
            _app_errors.RepositoryORMNotFoundError,
            _api_v1_handlers.not_found_exception_handler,
        )
        fastapi_app.add_exception_handler(_app_errors.RepositoryError, _api_v1_handlers.repository_exception_handler)
        fastapi_app.add_exception_handler(
            _app_errors.ServiceAuthorizationError,
            _api_v1_handlers.authorization_exception_handler,
        )
        fastapi_app.add_exception_handler(_app_errors.ServiceError, _api_v1_handlers.service_exception_handler)

        application = Application(
            settings=settings,
            fastapi_app=fastapi_app,
            disposable_resources=disposable_resources,
        )

        logger.info("Initializing application finished")

        return application

    async def start(self) -> None:
        try:
            config = uvicorn.Config(
                app=self._fastapi_app,
                host=self._settings.api.host,
                port=self._settings.api.port,
            )
            server = uvicorn.Server(config)
            await server.serve()
        except BaseException as unexpected_error:
            logger.exception("FastAPI failed to start")
            msg = "FastAPI failed to start"
            raise _app_errors.StartServerError(msg) from unexpected_error

    async def dispose(self) -> None:
        logger.info("Application is shutting down...")
        dispose_errors: list[BaseException] = []

        for resource in self._disposable_resources:
            logger.info("Disposing %s...", resource.name)
            try:
                await resource.dispose_callback
            except Exception as unexpected_error:
                dispose_errors.append(unexpected_error)
                logger.exception("Failed to dispose %s", resource.name)
            else:
                logger.info("%s has been disposed", resource.name)

        if len(dispose_errors) != 0:
            logger.error("Application has shut down with errors")
            msg = "Application has shut down with errors, see logs above"
            raise _app_errors.DisposeError(msg)

        logger.info("Application has successfully shut down")


__all__ = ["Application"]
