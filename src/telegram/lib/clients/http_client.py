import typing

import httpx

import lib.app.split_settings as app_split_settings


class AsyncHttpClient(httpx.AsyncClient):
    def __init__(
        self,
        proxy_settings: app_split_settings.ProxyBaseSettings | None = None,
        base_url: str | None = None,
        **client_params: typing.Any,
    ) -> None:
        self.base_url = base_url if base_url else ""
        self.proxy_settings = proxy_settings
        self.proxies = self.__get_proxies_from_settings()
        self.client_params = client_params

        super().__init__(base_url=self.base_url, proxies=self.proxies, **client_params)  # type: ignore

    def __get_proxies_from_settings(self) -> dict[str, str] | None:
        if not (self.proxy_settings and self.proxy_settings.enable):
            return None
        proxies = {"all://": self.proxy_settings.dsn}
        return proxies

    async def close(self) -> None:
        await self.aclose()
