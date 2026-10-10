import logging
from collections.abc import AsyncIterator
from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.exc import IntegrityError

from core.dependencies import get_db
from core.middleware import ProblemMiddleware

pytestmark = pytest.mark.anyio

ORIGIN = "http://client.test"


async def broken_db() -> AsyncIterator[None]:
    raise RuntimeError("boom")
    yield


@pytest.fixture
def failing_app(app: FastAPI) -> AsyncIterator[FastAPI]:
    app.dependency_overrides[get_db] = broken_db
    yield app
    app.dependency_overrides.clear()


async def test_unhandled_exception_is_a_problem_response(failing_app: FastAPI, async_client: AsyncClient) -> None:
    response = await async_client.get("/api/v1/categories")

    assert response.status_code == 500
    assert response.headers["content-type"] == "application/problem+json"
    assert response.json() == {
        "type": "about:blank",
        "title": "Internal Server Error",
        "status": 500,
        "detail": "Internal Server Error",
        "code": "internal_error",
        "request_id": response.headers["x-request-id"],
    }


async def test_unhandled_exception_keeps_middleware_headers(failing_app: FastAPI, async_client: AsyncClient) -> None:
    response = await async_client.get("/api/v1/categories", headers={"Origin": ORIGIN})

    assert response.headers["x-request-id"]
    assert response.headers["access-control-allow-origin"] == ORIGIN
    assert "x-process-time" in response.headers


async def test_unhandled_exception_is_logged_once_with_traceback(
    failing_app: FastAPI, async_client: AsyncClient, caplog
) -> None:
    with caplog.at_level(logging.INFO):
        await async_client.get("/api/v1/categories")

    (problem,) = [r for r in caplog.records if r.name == "core.problems"]
    assert problem.levelno == logging.ERROR
    assert problem.exc_info is not None
    assert "route=/api/v1/categories exc=RuntimeError" in problem.getMessage()
    assert any(r.getMessage().startswith("Outgoing response:") for r in caplog.records)


async def test_database_outage_is_503_with_retry_after(app: FastAPI, async_client: AsyncClient, caplog) -> None:
    async def unreachable_db() -> AsyncIterator[None]:
        raise ConnectionRefusedError("Connect call failed ('127.0.0.1', 5432)")
        yield

    app.dependency_overrides[get_db] = unreachable_db
    try:
        with caplog.at_level(logging.INFO, logger="core.problems"):
            response = await async_client.get("/api/v1/categories")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 503
    assert response.headers["retry-after"] == "5"
    assert response.json()["code"] == "service_unavailable"
    assert response.json()["detail"] == "Service temporarily unavailable"
    (record,) = caplog.records
    assert record.levelno == logging.ERROR
    assert record.exc_info is None


class EmptySession:
    async def execute(self, statement):
        return SimpleNamespace(scalars=lambda: SimpleNamespace(all=lambda: []))


async def test_constraint_violation_at_commit_is_409_without_row_data_in_logs(
    app: FastAPI, async_client: AsyncClient, caplog
) -> None:
    class UniqueViolation(Exception):
        sqlstate = "23505"

    async def db_failing_at_commit() -> AsyncIterator[EmptySession]:
        yield EmptySession()
        raise IntegrityError("INSERT", {}, UniqueViolation("DETAIL: Key (email)=(bob@example.com) already exists."))

    app.dependency_overrides[get_db] = db_failing_at_commit
    try:
        with caplog.at_level(logging.INFO):
            response = await async_client.get("/api/v1/categories")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 409
    assert response.json()["code"] == "already_exists"
    assert "bob@example.com" not in caplog.text
    assert "bob@example.com" not in response.text


async def test_error_after_response_started_is_logged_and_reraised(caplog) -> None:
    async def streaming_app(scope, receive, send) -> None:
        await send({"type": "http.response.start", "status": 200, "headers": []})
        raise RuntimeError("mid-stream")

    sent: list[dict] = []

    async def send(message: dict) -> None:
        sent.append(message)

    async def receive() -> dict:
        return {"type": "http.request"}

    with caplog.at_level(logging.INFO, logger="core.middleware"), pytest.raises(RuntimeError, match="mid-stream"):
        await ProblemMiddleware(streaming_app)({"type": "http", "method": "GET"}, receive, send)

    assert [m["type"] for m in sent] == ["http.response.start"]
    assert caplog.records[0].exc_info is not None
    (record,) = caplog.records
    assert record.levelno == logging.ERROR
    assert "problem after response started" in record.getMessage()


async def test_database_error_after_response_started_is_reraised_without_its_message(caplog) -> None:
    class DriverError(Exception):
        sqlstate = "23502"

    secret = "bob" + "@example.com"
    error = IntegrityError("INSERT", {}, DriverError(f"DETAIL: Failing row contains ({secret})"))

    async def streaming_app(scope, receive, send) -> None:
        await send({"type": "http.response.start", "status": 200, "headers": []})
        raise error

    async def send(message: dict) -> None:
        pass

    with caplog.at_level(logging.INFO, logger="core.problems"), pytest.raises(RuntimeError) as raised:
        await ProblemMiddleware(streaming_app)({"type": "http", "method": "GET"}, None, send)

    assert str(raised.value) == "IntegrityError: message withheld"
    assert raised.value.__suppress_context__
    assert secret not in caplog.text


async def test_non_http_scopes_pass_through() -> None:
    seen: list[str] = []

    async def inner(scope, receive, send) -> None:
        seen.append(scope["type"])
        raise RuntimeError("lifespan failure")

    with pytest.raises(RuntimeError, match="lifespan failure"):
        await ProblemMiddleware(inner)({"type": "lifespan"}, None, None)

    assert seen == ["lifespan"]
