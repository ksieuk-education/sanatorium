"""Настройки баз данных"""

import pydantic
import pydantic_settings

import lib.app.split_settings.utils as app_split_settings_utils


class DatabaseSettings(pydantic_settings.BaseSettings):
    """Настройки для подключения к базе данных, определение настроек сессии"""

    model_config = pydantic_settings.SettingsConfigDict(
        env_file=app_split_settings_utils.ENV_PATH,
        env_prefix="DB_",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Connection settings
    driver: str = "postgresql+asyncpg"
    name: str = "database_name"
    host: str = "localhost"
    port: int = 5432
    user: str = "app"
    password: pydantic.SecretStr = pydantic.Field(default=...)

    # Engine settings
    pool_size: int = 50
    pool_pre_ping: bool = True
    echo: bool = False

    # Session settings
    auto_commit: bool = False
    auto_flush: bool = False
    expire_on_commit: bool = False

    @property
    def dsn(self) -> str:
        password = self.password.get_secret_value()
        return f"{self.driver}://{self.user}:{password}@{self.host}:{self.port}/{self.name}"

    @property
    def dsn_as_safe_url(self) -> str:
        return f"{self.driver}://{self.user}:***@{self.host}:{self.port}"
