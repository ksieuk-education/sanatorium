import typing

import pydantic
import pydantic_settings

import lib.app.split_settings.utils as app_split_settings_utils


class AppSettings(pydantic_settings.BaseSettings):
    model_config = pydantic_settings.SettingsConfigDict(
        env_file=app_split_settings_utils.ENV_PATH,
        env_file_encoding="utf-8",
        env_prefix="APP_",
        extra="ignore",
    )

    admin_ids: set[int] = pydantic.Field(default=...)

    @pydantic.model_validator(mode="before")  # type: ignore[reportArgumentType]
    @classmethod
    def required_one(cls, values: dict[str, typing.Any]) -> dict[str, typing.Any]:
        if "admin_ids" in values:
            if isinstance(values["admin_ids"], str | int):
                values["admin_ids"] = set(map(int, str(values["admin_ids"]).split(",")))
        return values
