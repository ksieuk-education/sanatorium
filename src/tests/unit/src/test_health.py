import http

import httpx
import pytest

pytestmark = [pytest.mark.asyncio]


async def test_health(app_http_client: httpx.AsyncClient) -> None:
    response = await app_http_client.get("/health/")
    assert response.status_code == http.HTTPStatus.OK
