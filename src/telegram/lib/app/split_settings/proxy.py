import typing

import pydantic
import pydantic_settings

import lib.app.split_settings.utils as app_split_settings_utils


class ProxyBaseSettings(pydantic_settings.BaseSettings):
    model_config = pydantic_settings.SettingsConfigDict(
        env_file=app_split_settings_utils.ENV_PATH,
        env_prefix="PROXY_",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    protocol: typing.Literal["http", "socks5"] = "http"
    user: str | None = None
    password: pydantic.SecretStr | None = None
    host: str | None = None
    port: int | None = None
    enable: bool = False

    @property
    def dsn(self) -> str:
        if self.user and self.password:
            password = self.password.get_secret_value()
            return f"{self.protocol}://{self.user}:{password}@{self.host}:{self.port}"
        return f"{self.protocol}://{self.host}:{self.port}"

    @pydantic.computed_field
    @property
    def dsn_as_safe_url(self) -> str:
        if self.user and self.password:
            return f"{self.protocol}://{self.user}:{self.password}@{self.host}:{self.port}"
        return f"{self.protocol}://{self.host}:{self.port}"

    @pydantic.model_validator(mode="after")
    def check_proxy(self):
        if not self.enable:
            return self
        if self.host and self.port:
            return self
        raise ValueError("Proxy settings must be set if use_proxy is True")
