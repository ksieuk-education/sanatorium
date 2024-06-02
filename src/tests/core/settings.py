import logging
import typing

import pydantic
import pydantic_settings
import yaml

import tests.core.split_settings as _core_split_settings

logger = logging.getLogger(__name__)


class TestsSettings(pydantic_settings.BaseSettings):
    """
    Настройки, собранные вместе.
    """

    model_config = pydantic_settings.SettingsConfigDict(
        env_file=_core_split_settings.ENV_PATH,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    use_config_yml: bool = True

    test_api: _core_split_settings.ApiSettings = pydantic.Field(default_factory=_core_split_settings.ApiSettings)
    test_project: _core_split_settings.ProjectSettings = pydantic.Field(
        default_factory=_core_split_settings.ProjectSettings
    )

    @pydantic.model_validator(mode="before")
    @classmethod
    def load_from_config_yml(cls, values: dict[str, typing.Any]) -> dict[str, typing.Any]:
        config_path = _core_split_settings.CONFIG_YML_PATH
        use_config_yml: bool | str = values.get("use_config_yml", True)
        if isinstance(use_config_yml, str):
            use_config_yml = use_config_yml.lower() == "true"

        if not use_config_yml:
            return values
        if not config_path.exists():
            logger.error("Config file does not exist")
            return values

        with config_path.open(encoding="utf-8") as file:
            data = yaml.safe_load(file)
        values.update(data)
        return values


tests_settings = TestsSettings()
