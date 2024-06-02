import http

import pytest

import tests.functional.models as tests_functional_models

pytestmark = [pytest.mark.asyncio]


async def test_health(
    make_request: tests_functional_models.MakeResponseCallableType,
) -> None:
    response = await make_request(
        method=tests_functional_models.MethodsEnum.GET,
        api_method="/health/",
    )
    assert response.status_code == http.HTTPStatus.OK
