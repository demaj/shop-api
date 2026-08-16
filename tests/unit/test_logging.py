import logging
import uuid

import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.anyio


def _incoming(records: list[logging.LogRecord]) -> str:
    messages = [r.getMessage() for r in records if r.getMessage().startswith("Incoming request:")]
    assert messages, "no 'Incoming request' log was captured"
    return messages[0]


async def test_request_log_has_generated_correlation_id(async_client: AsyncClient, caplog) -> None:
    # No X-Request-Id sent — the middleware generates one, and it must reach the log.
    with caplog.at_level(logging.INFO, logger="main"):
        response = await async_client.get("/")
    assert response.status_code == 200
    assert "None" not in _incoming(caplog.records)


async def test_request_log_uses_client_correlation_id(async_client: AsyncClient, caplog) -> None:
    correlation_id = str(uuid.uuid4())
    with caplog.at_level(logging.INFO, logger="main"):
        await async_client.get("/", headers={"X-Request-Id": correlation_id})
    assert correlation_id in _incoming(caplog.records)
