from collections.abc import Iterator

import pytest
from fastapi import FastAPI
from httpx import AsyncClient

import models
from core import security
from core.dependencies import get_current_user
from routers.auth import login_candidate

pytestmark = pytest.mark.anyio

EMAIL = "inactive@example.com"
PASSWORD = "correct-password"


@pytest.fixture
def inactive_user(app: FastAPI) -> Iterator[models.User]:
    user = models.User(email=EMAIL, hashed_password=security.hash_password_sync(PASSWORD), is_active=False)
    app.dependency_overrides[login_candidate] = lambda: user
    app.dependency_overrides[get_current_user] = lambda: user
    yield user
    app.dependency_overrides.clear()


async def login(client: AsyncClient, password: str):
    return await client.post("/api/v1/auth/token", data={"username": EMAIL, "password": password})


async def test_inactive_login_is_indistinguishable_from_a_wrong_password(
    inactive_user: models.User, async_client: AsyncClient
) -> None:
    correct = await login(async_client, PASSWORD)
    wrong = await login(async_client, "wrong-password")

    assert correct.status_code == wrong.status_code == 401
    assert correct.headers["www-authenticate"] == "Bearer"
    assert correct.json()["code"] == "invalid_credentials"
    without_request_id = [{k: v for k, v in r.json().items() if k != "request_id"} for r in (correct, wrong)]
    assert without_request_id[0] == without_request_id[1]


async def test_token_of_an_inactive_user_is_403(inactive_user: models.User, async_client: AsyncClient) -> None:
    response = await async_client.get("/api/v1/users/me", headers={"Authorization": "Bearer any"})

    assert response.status_code == 403
    assert response.json()["code"] == "account_inactive"
