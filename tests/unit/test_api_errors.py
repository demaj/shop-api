from collections.abc import AsyncIterator, Iterator

import pytest
from fastapi import FastAPI
from httpx import AsyncClient

import crud
import models
from core import security
from core.dependencies import get_current_user, get_db

pytestmark = pytest.mark.anyio

MISSING = "00000000-0000-0000-0000-000000000000"
AUTH = {"Authorization": "Bearer any"}


class EmptySession:
    async def get(self, model, id):
        return None


async def empty_db() -> AsyncIterator[EmptySession]:
    yield EmptySession()


@pytest.fixture
def plain_user(app: FastAPI) -> Iterator[None]:
    user = models.User(email="user@example.com", hashed_password="x", is_active=True, is_superuser=False)
    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_db] = empty_db
    yield
    app.dependency_overrides.clear()


async def test_garbage_token_is_unauthenticated(async_client: AsyncClient) -> None:
    response = await async_client.get("/api/v1/users/me", headers={"Authorization": "Bearer garbage"})

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"
    assert response.json()["code"] == "unauthenticated"


@pytest.mark.parametrize("resource", ["categories", "products"])
async def test_missing_resource_is_resource_not_found(
    plain_user: None, async_client: AsyncClient, resource: str
) -> None:
    response = await async_client.get(f"/api/v1/{resource}/{MISSING}")

    assert response.status_code == 404
    assert response.json()["code"] == "resource_not_found"
    assert MISSING in response.json()["detail"]


async def test_unknown_route_is_still_route_not_found(async_client: AsyncClient) -> None:
    response = await async_client.get("/api/v1/nope")

    assert response.json()["code"] == "route_not_found"


@pytest.mark.parametrize("resource", ["categories", "products"])
async def test_empty_update_is_validation_failed(plain_user: None, async_client: AsyncClient, resource: str) -> None:
    response = await async_client.put(f"/api/v1/{resource}/{MISSING}", json={}, headers=AUTH)

    assert response.status_code == 422
    assert response.json()["code"] == "validation_failed"
    assert response.json()["detail"] == "No updatable fields provided"


async def test_non_superuser_is_forbidden(plain_user: None, async_client: AsyncClient) -> None:
    response = await async_client.post(
        "/api/v1/users", json={"email": "new@example.com", "password": "password123"}, headers=AUTH
    )

    assert response.status_code == 403
    assert response.json()["code"] == "forbidden"


async def test_token_of_a_deleted_user_looks_like_a_bad_token(app: FastAPI, async_client: AsyncClient) -> None:
    app.dependency_overrides[get_db] = empty_db
    try:
        token = security.create_access_token(MISSING)
        deleted = await async_client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token}"})
        garbage = await async_client.get("/api/v1/users/me", headers={"Authorization": "Bearer garbage"})
    finally:
        app.dependency_overrides.clear()

    assert deleted.status_code == garbage.status_code == 401
    assert deleted.headers["www-authenticate"] == garbage.headers["www-authenticate"] == "Bearer"
    without_request_id = [{k: v for k, v in r.json().items() if k != "request_id"} for r in (deleted, garbage)]
    assert without_request_id[0] == without_request_id[1]
    assert deleted.json()["code"] == "unauthenticated"


async def test_duplicate_email_is_already_exists(app: FastAPI, async_client: AsyncClient, monkeypatch) -> None:
    existing = models.User(email="taken@example.com", hashed_password="x", is_active=True, is_superuser=True)

    async def get_by_email(db, *, email: str) -> models.User:
        return existing

    monkeypatch.setattr(crud.user, "get_by_email", get_by_email)
    app.dependency_overrides[get_current_user] = lambda: existing
    app.dependency_overrides[get_db] = empty_db
    try:
        response = await async_client.post(
            "/api/v1/users", json={"email": "taken@example.com", "password": "password123"}, headers=AUTH
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 409
    assert response.json()["code"] == "already_exists"
