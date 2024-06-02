import asyncio
import typing

import fastapi
import httpx
import pytest_asyncio

import lib.app.app as lib_app
import lib.app.settings as _settings
import tests.core.settings as _core_settings
import tests.functional.models as functional_models


@pytest_asyncio.fixture  # type: ignore[reportUntypedFunctionDecorator]
async def http_client(
    base_url: str = _core_settings.tests_settings.test_api.get_api_url,
) -> typing.AsyncGenerator[httpx.AsyncClient, typing.Any]:
    session = httpx.AsyncClient(base_url=base_url)
    yield session
    await session.aclose()


@pytest_asyncio.fixture  # type: ignore[reportUntypedFunctionDecorator]
async def make_request(
    http_client: httpx.AsyncClient,  # pylint: disable=dangerous-default-value,redefined-outer-name
) -> typing.Callable[..., typing.Awaitable[functional_models.HTTPResponse]]:
    async def inner(  # pylint: disable=dangerous-default-value
        api_method: str = "",
        method: functional_models.MethodsEnum = functional_models.MethodsEnum.GET,
        headers: dict[str, str] = _core_settings.tests_settings.test_api.headers,
        body: dict[str, typing.Any] | None = None,
        jwt_token: str | None = None,
    ) -> functional_models.HTTPResponse:
        if jwt_token is not None:
            headers["Authorization"] = f"Bearer {jwt_token}"

        client_params = {"json": body, "headers": headers}
        if method == functional_models.MethodsEnum.GET:
            del client_params["json"]

        response = await getattr(http_client, method.value)(api_method, **client_params)
        return functional_models.HTTPResponse(
            body=response.json(),
            headers=response.headers,
            status_code=response.status_code,
        )

    return inner


@pytest_asyncio.fixture(scope="session")  # type: ignore[reportUntypedFunctionDecorator]
def app() -> fastapi.FastAPI:  # pylint: disable=redefined-outer-name
    settings = _settings.Settings()
    application = lib_app.Application.from_settings(settings)
    return application._fastapi_app  # type: ignore[reportPrivateUsage]  # noqa: SLF001


@pytest_asyncio.fixture  # type: ignore[reportUntypedFunctionDecorator]
async def app_http_client(
    app: fastapi.FastAPI,  # pylint: disable=redefined-outer-name
    base_url: str = _core_settings.tests_settings.test_api.get_api_url,
) -> typing.AsyncGenerator[httpx.AsyncClient, typing.Any]:
    session = httpx.AsyncClient(app=app, base_url=base_url)
    yield session
    await session.aclose()


@pytest_asyncio.fixture(scope="session")  # type: ignore[reportUntypedFunctionDecorator]
def event_loop() -> typing.Generator[asyncio.AbstractEventLoop, None, None]:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
