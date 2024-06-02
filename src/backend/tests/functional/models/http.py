import dataclasses
import enum
import typing

import multidict

import tests.core.settings as functional_settings


class MethodsEnum(enum.Enum):
    """
    Enumeration of methods.
    """

    GET = "get"
    POST = "post"
    PUT = "put"
    DELETE = "delete"
    PATCH = "patch"


@dataclasses.dataclass
class HTTPResponse:
    """
    Represents a HTTP response.
    """

    body: dict[str, typing.Any] | str
    headers: multidict.CIMultiDictProxy[str]
    status_code: int


class MakeResponseCallableType(typing.Protocol):
    """
    Protocol for making a response callable.
    """

    async def __call__(  # pylint: disable=dangerous-default-value  # noqa: PLR0913
        self,
        api_method: str = "",
        url: str = functional_settings.tests_settings.test_api.get_api_url,
        method: MethodsEnum = MethodsEnum.GET,
        headers: dict[str, str] = functional_settings.tests_settings.test_api.headers,
        body: dict[str, typing.Any] | None = None,
        jwt_token: str | None = None,
    ) -> HTTPResponse:
        ...
