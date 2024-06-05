import pydantic_settings

import lib.app.split_settings as app_split_settings


class Settings(pydantic_settings.BaseSettings):
    app: app_split_settings.AppSettings = app_split_settings.AppSettings()
    logger: app_split_settings.LoggerSettings = app_split_settings.LoggerSettings()
    project: app_split_settings.ProjectSettings = app_split_settings.ProjectSettings()
    redis: app_split_settings.RedisSettings = app_split_settings.RedisSettings()
    proxy: app_split_settings.ProxyBaseSettings = app_split_settings.ProxyBaseSettings()
