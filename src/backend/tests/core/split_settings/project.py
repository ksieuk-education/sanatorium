import pydantic_settings

import lib.app.split_settings.utils as app_split_settings_utils


class ProjectSettings(pydantic_settings.BaseSettings):
    """
    Общие настройки.
    """

    model_config = pydantic_settings.SettingsConfigDict(
        env_file=app_split_settings_utils.ENV_PATH,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    debug: bool = False
