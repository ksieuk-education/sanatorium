import dataclasses
import logging
import logging.config as logging_config
import typing

import aiogram
import aiogram.fsm.storage.memory as aiogram_fsm_storage_memory

import lib.app.errors as app_errors
import lib.app.settings as app_settings
import lib.app.split_settings as app_split_settings
import lib.clients as clients
import lib.routers as routers
import lib.sanatorium.services as media_services

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class DisposableResource:
    name: str
    dispose_callback: typing.Awaitable[typing.Any]


class Application:
    def __init__(
        self,
        settings: app_settings.Settings,
        bot: aiogram.Bot,
        dispatcher: aiogram.Dispatcher,
        disposable_resources: list[DisposableResource],
    ):
        self._settings = settings
        self._bot = bot
        self._dispatcher = dispatcher
        self._disposable_resources = disposable_resources

    @classmethod
    def from_settings(cls, settings: app_settings.Settings) -> "Application":
        # Logging

        logging_config.dictConfig(app_split_settings.get_logging_config(**settings.logger.model_dump()))
        if not settings.project.debug:
            logging.getLogger("aiogram").setLevel(logging.WARNING)

        logger.info("Initializing application")
        disposable_resources: list[DisposableResource] = []

        # Global clients

        logger.info("Initializing global clients")

        bot = aiogram.Bot(token=settings.project.bot_token.get_secret_value())
        http_client = clients.AsyncHttpClient(base_url=settings.project.sanatorium_api_url)

        # General Routers
        general_router = routers.GeneralRouter(bot)

        # Clients
        logger.info("Initializing clients")

        # Repositories

        logger.info("Initializing repositories")

        # Caches

        logger.info("Initializing caches")

        redis_client = clients.RedisAsyncClient(settings.redis)

        # Services

        logger.info("Initializing services")

        user_service = media_services.UserService(http_client=http_client)

        # States

        logger.info("Initializing states")

        # governor_collection = _structures_collections.Collection(redis_storage, settings.app.governor_collection_name)

        # Filters

        logger.info("Initializing filters")

        # Routers

        logger.info("Initializing routers")

        base_router = aiogram.Router()

        admin_base_router = aiogram.Router()

        media_base_router = aiogram.Router()

        routers.StartRouter(base_router)
        routers.UserCreateRouter(base_router, user_service)
        # routers.GovernorRouter(admin_base_router, governor_collection)
        # routers.MediaStartRouter(media_base_router, media_service)
        # routers.MediaCreateRouter(media_base_router, media_service)
        # routers.MediaGetRouter(media_base_router, media_service)
        # routers.MediaRunRouter(media_base_router, media_service)

        logger.info("Creating application")

        dispatcher = aiogram.Dispatcher(storage=aiogram_fsm_storage_memory.MemoryStorage())

        # Routes include

        dispatcher.include_routers(
            base_router,
            admin_base_router,
            media_base_router,
        )

        application = Application(
            settings=settings,
            bot=bot,
            dispatcher=dispatcher,
            disposable_resources=disposable_resources,
        )

        logger.info("Initializing application finished")

        return application

    async def start(self) -> None:
        try:
            await self._bot.delete_webhook(drop_pending_updates=True)
            await self._dispatcher.start_polling(self._bot)
        except BaseException as unexpected_error:
            logger.exception("FastAPI failed to start")
            raise app_errors.StartServerError("FastAPI failed to start") from unexpected_error

    async def dispose(self) -> None:
        logger.info("Application is shutting down...")
        dispose_errors: list[BaseException] = []

        for resource in self._disposable_resources:
            logger.info("Disposing %s...", resource.name)
            try:
                await resource.dispose_callback
            except Exception as unexpected_error:
                dispose_errors.append(unexpected_error)
                logger.error("Failed to dispose %s", resource.name)
            else:
                logger.info("%s has been disposed", resource.name)

        logger.info("Stopping polling...")
        try:
            await self._dispatcher.stop_polling()
        except Exception as unexpected_error:
            dispose_errors.append(unexpected_error)
            logger.error("Failed to dispose dispatcher")

        if len(dispose_errors) != 0:
            logger.error("Application has shut down with errors")
            raise app_errors.DisposeError("Application has shut down with errors, see logs above")

        logger.info("Application has successfully shut down")
