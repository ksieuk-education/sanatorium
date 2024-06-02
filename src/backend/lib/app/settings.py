"""Настройки проекта"""

import logging
import typing

import pydantic
import pydantic_settings
import yaml

import lib.app.split_settings as _app_split_settings

logger_ = logging.getLogger(__name__)


class Settings(pydantic_settings.BaseSettings):
    """Настройки проекта"""

    model_config = pydantic_settings.SettingsConfigDict(
        env_file=_app_split_settings.ENV_PATH,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    use_config_yml: bool = True

    api: _app_split_settings.ApiSettings = pydantic.Field(default_factory=_app_split_settings.ApiSettings)
    app: _app_split_settings.AppSettings = pydantic.Field(default_factory=_app_split_settings.AppSettings)
    logger: _app_split_settings.LoggingSettings = pydantic.Field(default_factory=_app_split_settings.LoggingSettings)
    database: _app_split_settings.DatabaseSettings = pydantic.Field(
        default_factory=_app_split_settings.DatabaseSettings
    )

    @pydantic.model_validator(mode="before")
    @classmethod
    def load_from_config_yml(cls, values: dict[str, typing.Any]) -> dict[str, typing.Any]:
        """
        Загрузка настроек из config.yml

        :param values: Значения настроек, переданные при инициализации класса.
        При загрузке из .yml файла ожидается параметр use_config_yml=True
        """

        config_path = _app_split_settings.CONFIG_YML_PATH
        use_config_yml: bool | str = values.get("use_config_yml", True)
        if isinstance(use_config_yml, str):
            use_config_yml = use_config_yml.lower() == "true"

        if not use_config_yml:
            return values
        if not config_path.exists():
            logger_.error("Config file does not exist")
            return values

        with config_path.open(encoding="utf-8") as file:
            data = yaml.safe_load(file)
        values.update(data)
        return values
