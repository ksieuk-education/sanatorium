import pydantic
import pydantic_settings

import lib.app.split_settings.utils as app_split_settings_utils


class RedisSettings(pydantic_settings.BaseSettings):
    """Project settings."""

    model_config = pydantic_settings.SettingsConfigDict(
        env_file=app_split_settings_utils.ENV_PATH,
        env_file_encoding="utf-8",
        env_prefix="REDIS_",
        extra="ignore",
    )

    protocol: str = "redis"
    host: str = "localhost"
    port: int = 6379
    password: pydantic.SecretStr = pydantic.Field(default=...)
    database: str = "0"

    def get_dsn(self):
        password = self.password.get_secret_value()
        return f"{self.protocol}://user:{password}@{self.host}:{self.port}/{self.database}"
