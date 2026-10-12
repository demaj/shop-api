import threading
import time
from collections.abc import Iterator

import anyio
import pytest
from fastapi import FastAPI
from httpx import AsyncClient

import models
from core import security
from core.config import get_settings
from routers.auth import login_candidate
from schemas.user import PASSWORD_MAX_LENGTH

pytestmark = pytest.mark.anyio


def test_hash_concurrency_default() -> None:
    assert get_settings().PASSWORD_HASH_CONCURRENCY == 4


async def test_password_hashing_never_exceeds_the_concurrency_limit(monkeypatch) -> None:
    limit = get_settings().PASSWORD_HASH_CONCURRENCY
    lock = threading.Lock()
    running = 0
    peak = 0

    def slow_verify(password: str, hashed_password: str) -> bool:
        nonlocal running, peak
        with lock:
            running += 1
            peak = max(peak, running)
        time.sleep(0.05)
        with lock:
            running -= 1
        return False

    monkeypatch.setattr(security, "verify_password_sync", slow_verify)

    async with anyio.create_task_group() as group:
        for _ in range(limit * 5):
            group.start_soon(security.verify_password, "password", "hash")
            group.start_soon(security.verify_dummy_password, "password")

    assert peak == limit


@pytest.fixture
def known_user(app: FastAPI) -> Iterator[None]:
    user = models.User(email="user@example.com", hashed_password="x", is_active=True)
    app.dependency_overrides[login_candidate] = lambda: user
    yield
    app.dependency_overrides.clear()


async def test_overlong_password_is_rejected_without_hashing(
    known_user: None, async_client: AsyncClient, monkeypatch
) -> None:
    def must_not_hash(*args: object) -> bool:
        raise AssertionError("an over-long password reached the hasher")

    monkeypatch.setattr(security, "verify_password_sync", must_not_hash)

    response = await async_client.post(
        "/api/v1/auth/token", data={"username": "user@example.com", "password": "x" * (PASSWORD_MAX_LENGTH + 1)}
    )

    assert response.status_code == 401
    assert response.json()["code"] == "invalid_credentials"


async def test_password_at_the_limit_is_still_verified(
    known_user: None, async_client: AsyncClient, monkeypatch
) -> None:
    seen: list[int] = []
    monkeypatch.setattr(security, "verify_password_sync", lambda password, hashed: seen.append(len(password)) or False)

    response = await async_client.post(
        "/api/v1/auth/token", data={"username": "user@example.com", "password": "x" * PASSWORD_MAX_LENGTH}
    )

    assert response.status_code == 401
    assert seen == [PASSWORD_MAX_LENGTH]
