from http import HTTPStatus

import pytest
from httpx import AsyncClient

BASE_URL = "/categories"


@pytest.mark.anyio
async def test_read_categories(async_client: AsyncClient) -> None:
    response = await async_client.get(BASE_URL)
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"status": "OK"}


@pytest.mark.anyio
async def test_create_category(async_client: AsyncClient) -> None:
    response = await async_client.post(BASE_URL)
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"status": "OK"}


@pytest.mark.anyio
async def test_update_category(async_client: AsyncClient) -> None:
    response = await async_client.post(BASE_URL)
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"status": "OK"}


@pytest.mark.anyio
async def test_delete_category(async_client: AsyncClient) -> None:
    response = await async_client.post(BASE_URL)
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"status": "OK"}
