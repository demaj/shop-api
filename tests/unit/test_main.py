from http import HTTPStatus

import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_main_app(async_client: AsyncClient) -> None:
    response = await async_client.get("/")
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"status": "OK"}
