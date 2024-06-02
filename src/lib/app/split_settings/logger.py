"""Настройки логирования"""

import pathlib
import typing

import pydantic
import pydantic_settings

import lib.app.split_settings.utils as app_split_settings_utils


class LoggingSettings(pydantic_settings.BaseSettings):
    """Настройки для логирования"""

    model_config = pydantic_settings.SettingsConfigDict(
        env_file=app_split_settings_utils.ENV_PATH,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_default_handlers: list[str] = [  # noqa: RUF012
        "console",
        "file",
    ]

    log_level_handlers: str = "INFO"
    log_level_loggers: str = "INFO"
    log_level_root: str = "INFO"
    log_file_path: pathlib.Path = app_split_settings_utils.BASE_PATH.parent / "logs" / "verbose.log"

    @pydantic.model_validator(mode="after")
    def check_directory_exist(self) -> typing.Self:
        dir_path = self.log_file_path.parent
        if not dir_path.exists():
            dir_path.mkdir()
        return self


def get_logging_config(  # noqa: PLR0913
    log_format: str,
    log_default_handlers: list[str],
    log_level_handlers: str,
    log_level_loggers: str,
    log_level_root: str,
    log_file_path: pathlib.Path,
) -> dict[str, typing.Any]:
    """
    Получения конфига для логирования

    :param log_format: Формат логов
    :param log_default_handlers: Хэндлеры по умолчанию
    :param log_level_handlers: Уровень получения логов хэндлеров
    :param log_level_loggers: Уровень получения логов логеров
    :param log_level_root: Уровень получения рут логов
    :param log_file_path: Путь до файла, где будут сохраняться логи
    :return: Конфиг для логирования
    """

    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "verbose": {"format": log_format},
            "default": {
                "()": "uvicorn.logging.DefaultFormatter",
                "fmt": "%(levelprefix)s %(message)s",
                "use_colors": None,
            },
            "access": {
                "()": "uvicorn.logging.AccessFormatter",
                "fmt": "%(levelprefix)s %(client_addr)s - '%(request_line)s' %(status_code)s",
            },
            "http": {
                "format": "%(levelname)s [%(asctime)s] %(name)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "level": log_level_handlers,
                "class": "logging.StreamHandler",
                "formatter": "verbose",
            },
            "default": {
                "formatter": "default",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
            },
            "access": {
                "formatter": "access",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
            },
            "file": {
                "level": log_level_handlers,
                "formatter": "verbose",
                "class": "logging.handlers.RotatingFileHandler",
                "filename": log_file_path,
                "mode": "a",
                "maxBytes": 10485760,
                "backupCount": 7,
            },
        },
        "loggers": {
            "": {
                "handlers": log_default_handlers,
                "level": log_level_loggers,
            },
            "uvicorn.error": {
                "level": log_level_loggers,
            },
            "uvicorn.access": {
                "handlers": ["access"],
                "level": log_level_loggers,
                "propagate": False,
            },
            "httpx": {
                "handlers": ["default"],
                "level": log_level_loggers,
            },
            "httpcore": {
                "handlers": ["default"],
                "level": "DEBUG",
            },
        },
        "root": {
            "level": log_level_root,
            "formatter": "verbose",
            "handlers": log_default_handlers,
        },
    }
