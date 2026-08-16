import os
from importlib import reload

import pytest
from fastapi import FastAPI
from httpx import AsyncClient

os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ.setdefault("DATABASE_URI", "postgresql+asyncpg://test:test@localhost:5432/testdb")
os.environ.setdefault("FIRST_SUPERUSER", "admin@example.com")
os.environ.setdefault("FIRST_SUPERUSER_PASSWORD", "test-password")

BASE_URL = "http://api.shop.com"


@pytest.fixture
async def app():
    import shop_api.main

    reload(shop_api.main)
    yield shop_api.main.app


@pytest.fixture
async def async_client(app: FastAPI) -> AsyncClient:
    async with AsyncClient(app=app, base_url=BASE_URL) as async_client:
        yield async_client
