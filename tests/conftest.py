import os
from collections.abc import AsyncIterator

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

# Must run before any app import: get_settings() is lru_cached at first call.
os.environ.setdefault("SECRET_KEY", "0123456789abcdef" * 4)
os.environ.setdefault("DATABASE_URI", "postgresql+asyncpg://shop:shop@localhost:5432/shop_test")
os.environ.setdefault("FIRST_SUPERUSER", "admin@example.com")
os.environ.setdefault("FIRST_SUPERUSER_PASSWORD", "change-this-password")

BASE_URL = "http://api.shop.com"


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
def app() -> FastAPI:
    # Import as `main`, never `shop_api.main`: the app's own modules resolve as
    # top-level (`core.*`), and dependency_overrides must key on those objects.
    import main

    return main.app


@pytest.fixture
async def async_client(app: FastAPI) -> AsyncIterator[AsyncClient]:
    async with AsyncClient(transport=ASGITransport(app=app), base_url=BASE_URL) as client:
        yield client
