import pydantic
import pydantic_settings

import lib.app.split_settings.utils as app_split_settings_utils


class ProjectSettings(pydantic_settings.BaseSettings):
    """Project settings."""

    model_config = pydantic_settings.SettingsConfigDict(
        env_file=app_split_settings_utils.ENV_PATH,
        env_file_encoding="utf-8",
        env_prefix="PROJECT_",
        extra="ignore",
    )

    debug: bool = False
    bot_token: pydantic.SecretStr = pydantic.Field(default=...)
    sanatorium_protocol: str = "http"
    sanatorium_host: str = "localhost"
    sanatorium_port: int = 8000

    @pydantic.computed_field
    @property
    def sanatorium_api_url(self) -> str:
        return f"{self.sanatorium_protocol}://{self.sanatorium_host}:{self.sanatorium_port}/api/v1"
