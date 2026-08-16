"""401 checks need no database: the router-level auth dependency short-circuits before get_db."""

from http import HTTPStatus

import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.anyio

WRITE_ATTEMPTS = [
    ("post", "/api/v1/categories", {"name": "Nope"}),
    ("put", "/api/v1/categories/00000000-0000-0000-0000-000000000000", {"name": "Nope"}),
    ("delete", "/api/v1/categories/00000000-0000-0000-0000-000000000000", None),
    ("post", "/api/v1/products", {"name": "N", "price": 1, "category_id": "00000000-0000-0000-0000-000000000000"}),
    ("put", "/api/v1/products/00000000-0000-0000-0000-000000000000", {"price": 1}),
    ("delete", "/api/v1/products/00000000-0000-0000-0000-000000000000", None),
    ("get", "/api/v1/users/me", None),
    ("post", "/api/v1/users", {"email": "a@b.com", "password": "password123"}),
]


@pytest.mark.parametrize(("method", "path", "body"), WRITE_ATTEMPTS)
async def test_401_without_token(async_client: AsyncClient, method: str, path: str, body: dict | None) -> None:
    response = await async_client.request(method, path, json=body)
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.headers["WWW-Authenticate"] == "Bearer"


@pytest.mark.parametrize(("method", "path", "body"), WRITE_ATTEMPTS)
async def test_401_with_garbage_token(async_client: AsyncClient, method: str, path: str, body: dict | None) -> None:
    response = await async_client.request(method, path, json=body, headers={"Authorization": "Bearer garbage"})
    assert response.status_code == HTTPStatus.UNAUTHORIZED
