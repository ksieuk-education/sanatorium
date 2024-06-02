"""Настройки приложения"""

import pathlib

import pydantic_settings

import lib.app.split_settings.utils as app_split_settings_utils


class AppSettings(pydantic_settings.BaseSettings):
    """Настройки приложения"""

    model_config = pydantic_settings.SettingsConfigDict(
        env_file=app_split_settings_utils.ENV_PATH,
        env_prefix="APP_",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    title: str = "FastAPI"
    version: str = "0.1.0"
    docs_url: str = "/api/openapi"
    openapi_url: str = "/api/openapi.json"
    reload: bool = False
    debug: bool = False
    log_file_path: pathlib.Path = app_split_settings_utils.BASE_PATH / "logs"
