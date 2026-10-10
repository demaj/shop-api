import logging
import uuid

import pytest
from asgi_correlation_id import correlation_id
from httpx import AsyncClient

import main

pytestmark = pytest.mark.anyio


def _incoming(records: list[logging.LogRecord]) -> str:
    messages = [r.getMessage() for r in records if r.getMessage().startswith("Incoming request:")]
    assert messages, "no 'Incoming request' log was captured"
    return messages[0]


async def test_request_log_has_generated_correlation_id(async_client: AsyncClient, caplog) -> None:
    # No X-Request-Id sent — the middleware generates one, and it must reach the log.
    with caplog.at_level(logging.INFO, logger="core.middleware"):
        response = await async_client.get("/")
    assert response.status_code == 200
    assert "None" not in _incoming(caplog.records)


async def test_request_log_uses_client_correlation_id(async_client: AsyncClient, caplog) -> None:
    correlation_id = str(uuid.uuid4())
    with caplog.at_level(logging.INFO, logger="core.middleware"):
        await async_client.get("/", headers={"X-Request-Id": correlation_id})
    assert correlation_id in _incoming(caplog.records)


@pytest.fixture
def root_logging():
    root = logging.getLogger()
    handlers, level = root.handlers[:], root.level
    yield root
    root.handlers[:], root.level = handlers, level


def test_every_log_line_carries_the_correlation_id(root_logging: logging.Logger) -> None:
    main.configure_logging()
    (handler,) = root_logging.handlers
    record = logging.LogRecord("core.problems", logging.ERROR, __file__, 1, "problem status=500", None, None)

    token = correlation_id.set("9b1c")
    try:
        handler.filter(record)
        inside = handler.format(record)
    finally:
        correlation_id.reset(token)
    handler.filter(record)
    outside = handler.format(record)

    assert inside == "ERROR: core.problems: [9b1c] problem status=500"
    assert outside == "ERROR: core.problems: [-] problem status=500"
