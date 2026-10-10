import asyncpg
import pytest

from core.config import get_settings
from core.database import async_engine

pytestmark = pytest.mark.anyio


def test_timeout_defaults() -> None:
    settings = get_settings()

    assert settings.DATABASE_CONNECT_TIMEOUT == 5
    assert settings.DATABASE_POOL_TIMEOUT == 5
    assert settings.DATABASE_COMMAND_TIMEOUT == 30


def test_engine_bounds_pool_wait_and_hides_parameters() -> None:
    assert async_engine.pool.timeout() == get_settings().DATABASE_POOL_TIMEOUT
    assert async_engine.sync_engine.hide_parameters is True


async def test_driver_receives_connect_and_command_timeouts(monkeypatch) -> None:
    received: dict = {}

    async def recording_connect(*args, **kwargs):
        received.update(kwargs)
        raise ConnectionRefusedError("not connecting in a unit test")

    monkeypatch.setattr(asyncpg, "connect", recording_connect)

    with pytest.raises(ConnectionRefusedError):
        async with async_engine.connect():
            pass

    assert received["timeout"] == get_settings().DATABASE_CONNECT_TIMEOUT
    assert received["command_timeout"] == get_settings().DATABASE_COMMAND_TIMEOUT
