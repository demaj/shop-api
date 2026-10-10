"""End-to-end API flow against a real PostgreSQL (schema from `alembic upgrade head`).

Every test runs inside a rolled-back outer transaction — nothing persists.
"""

from collections.abc import Awaitable, Callable
from http import HTTPStatus

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncSession

import crud
from schemas import UserCreate

pytestmark = [pytest.mark.anyio, pytest.mark.integration]

SUPERUSER = {"email": "boss@example.com", "password": "boss-password"}
PLAIN_USER = {"email": "plain@example.com", "password": "plain-password"}


@pytest.fixture
def create_user(db_connection: AsyncConnection) -> Callable[..., Awaitable[None]]:
    async def _create(email: str, password: str, *, is_superuser: bool) -> None:
        async with AsyncSession(
            bind=db_connection, join_transaction_mode="create_savepoint", expire_on_commit=False
        ) as session:
            async with session.begin():
                await crud.user.create(
                    session,
                    obj_in=UserCreate(email=email, password=password, is_superuser=is_superuser),
                )

    return _create


@pytest.fixture
def login(async_client: AsyncClient) -> Callable[..., Awaitable[str]]:
    async def _login(email: str, password: str) -> str:
        response = await async_client.post("/api/v1/auth/token", data={"username": email, "password": password})
        assert response.status_code == HTTPStatus.OK, response.text
        return response.json()["access_token"]

    return _login


@pytest.fixture
async def superuser_auth(create_user, login) -> dict[str, str]:
    await create_user(**SUPERUSER, is_superuser=True)
    token = await login(**SUPERUSER)
    return {"Authorization": f"Bearer {token}"}


async def test_login_wrong_password_is_401(async_client: AsyncClient, create_user) -> None:
    await create_user(**SUPERUSER, is_superuser=True)
    response = await async_client.post(
        "/api/v1/auth/token", data={"username": SUPERUSER["email"], "password": "wrong"}
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED


async def test_users_me(async_client: AsyncClient, superuser_auth) -> None:
    response = await async_client.get("/api/v1/users/me", headers=superuser_auth)
    assert response.status_code == HTTPStatus.OK
    body = response.json()
    assert body["email"] == SUPERUSER["email"]
    assert body["is_superuser"] is True
    assert "hashed_password" not in body


async def test_authorized_crud_round_trip(async_client: AsyncClient, superuser_auth) -> None:
    created = await async_client.post("/api/v1/categories", json={"name": "Tea"}, headers=superuser_auth)
    assert created.status_code == HTTPStatus.CREATED
    category_id = created.json()["id"]

    product = await async_client.post(
        "/api/v1/products",
        json={"name": "Earl Grey", "price": 1999, "category_id": category_id},
        headers=superuser_auth,
    )
    assert product.status_code == HTTPStatus.CREATED
    assert product.json()["price"] == 1999
    assert product.json()["status"] == "available"

    updated = await async_client.put(
        f"/api/v1/products/{product.json()['id']}",
        json={"price": 2499, "status": "sold"},
        headers=superuser_auth,
    )
    assert updated.status_code == HTTPStatus.OK
    assert updated.json()["price"] == 2499
    assert updated.json()["updated"] is not None


async def test_duplicate_category_name_is_409(async_client: AsyncClient, superuser_auth) -> None:
    await async_client.post("/api/v1/categories", json={"name": "Tea"}, headers=superuser_auth)
    duplicate = await async_client.post("/api/v1/categories", json={"name": "Tea"}, headers=superuser_auth)
    assert duplicate.status_code == HTTPStatus.CONFLICT
    assert duplicate.json()["code"] == "already_exists"


async def test_unknown_category_fk_is_409(async_client: AsyncClient, superuser_auth) -> None:
    response = await async_client.post(
        "/api/v1/products",
        json={"name": "Ghost", "price": 1, "category_id": "00000000-0000-0000-0000-000000000000"},
        headers=superuser_auth,
    )
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json()["code"] == "reference_not_found"


async def test_delete_referenced_category_is_409(async_client: AsyncClient, superuser_auth) -> None:
    category = await async_client.post("/api/v1/categories", json={"name": "Tea"}, headers=superuser_auth)
    category_id = category.json()["id"]
    await async_client.post(
        "/api/v1/products",
        json={"name": "Earl Grey", "price": 1999, "category_id": category_id},
        headers=superuser_auth,
    )
    response = await async_client.delete(f"/api/v1/categories/{category_id}", headers=superuser_auth)
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json()["code"] == "resource_in_use"


async def test_non_superuser_cannot_create_users(async_client: AsyncClient, create_user, login) -> None:
    await create_user(**PLAIN_USER, is_superuser=False)
    token = await login(**PLAIN_USER)
    headers = {"Authorization": f"Bearer {token}"}

    forbidden = await async_client.post(
        "/api/v1/users", json={"email": "x@example.com", "password": "password123"}, headers=headers
    )
    assert forbidden.status_code == HTTPStatus.FORBIDDEN

    allowed = await async_client.post("/api/v1/categories", json={"name": "Coffee"}, headers=headers)
    assert allowed.status_code == HTTPStatus.CREATED


async def test_nul_byte_in_body_is_422_not_500(async_client: AsyncClient, superuser_auth) -> None:
    response = await async_client.post("/api/v1/categories", json={"name": "a\x00b"}, headers=superuser_auth)
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.json()["code"] == "validation_failed"


async def test_list_ordering_is_deterministic(async_client: AsyncClient, superuser_auth) -> None:
    for name in ("Zeta", "Alpha", "Midway"):
        await async_client.post("/api/v1/categories", json={"name": name}, headers=superuser_auth)
    first = await async_client.get("/api/v1/categories")
    second = await async_client.get("/api/v1/categories")
    names = [row["name"] for row in first.json()["results"]]
    assert names == sorted(names)
    assert first.json()["results"] == second.json()["results"]
