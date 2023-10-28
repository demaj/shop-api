from http import HTTPStatus

import pytest
from httpx import AsyncClient

BASE_URL = "/products"


@pytest.mark.anyio
async def test_read_products(async_client: AsyncClient) -> None:
    response = await async_client.get(BASE_URL)
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"status": "OK"}


@pytest.mark.anyio
async def test_create_products(async_client: AsyncClient) -> None:
    response = await async_client.post(BASE_URL)
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"status": "OK"}


@pytest.mark.anyio
async def test_update_products(async_client: AsyncClient) -> None:
    response = await async_client.post(BASE_URL)
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"status": "OK"}


@pytest.mark.anyio
async def test_delete_products(async_client: AsyncClient) -> None:
    response = await async_client.post(BASE_URL)
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"status": "OK"}
