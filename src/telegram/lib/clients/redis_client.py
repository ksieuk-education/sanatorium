import redis.asyncio as aioredis

import lib.app.split_settings as _app_split_settings


class RedisAsyncClient(aioredis.Redis):  # pylint: disable=too-many-ancestors,abstract-method
    """
    Асинхронный клиент для работы с Redis.
    """

    def __init__(self, settings: _app_split_settings.RedisSettings):
        self._settings = settings

        super().__init__(
            host=settings.host,
            port=settings.port,
            password=settings.password.get_secret_value(),
            db=settings.database,
        )

    async def dispose_callback(self):
        """
        Callback для закрытия соединения.
        """

        await self.aclose()
