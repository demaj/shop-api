import socket

import pytest
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.exc import TimeoutError as PoolTimeoutError

from core.errors import ErrorCode, classify


class DriverError(Exception):
    def __init__(self, sqlstate: str | None) -> None:
        super().__init__("driver message")
        self.sqlstate = sqlstate


def wrapped(sqlstate: str | None, cls: type[DBAPIError] = DBAPIError, invalidated: bool = False) -> DBAPIError:
    return cls("SELECT 1", {}, DriverError(sqlstate), connection_invalidated=invalidated)


@pytest.mark.parametrize(
    ("exc", "method", "code", "headers"),
    [
        (wrapped("23505", IntegrityError), "POST", ErrorCode.already_exists, {}),
        (wrapped("23503", IntegrityError), "POST", ErrorCode.reference_not_found, {}),
        (wrapped("23503", IntegrityError), "PUT", ErrorCode.reference_not_found, {}),
        (wrapped("23503", IntegrityError), "DELETE", ErrorCode.resource_in_use, {}),
        (wrapped("22001"), "POST", ErrorCode.validation_failed, {}),
        (wrapped("22003"), "POST", ErrorCode.validation_failed, {}),
        (wrapped("22021"), "POST", ErrorCode.validation_failed, {}),
        (wrapped("40001"), "POST", ErrorCode.service_unavailable, {"Retry-After": "1"}),
        (wrapped("40P01"), "POST", ErrorCode.service_unavailable, {"Retry-After": "1"}),
        (wrapped("57014"), "GET", ErrorCode.service_unavailable, {}),
        (TimeoutError(), "GET", ErrorCode.service_unavailable, {}),
        (wrapped("08006"), "GET", ErrorCode.service_unavailable, {"Retry-After": "5"}),
        (wrapped("53300"), "GET", ErrorCode.service_unavailable, {"Retry-After": "5"}),
        (wrapped("57P01"), "GET", ErrorCode.service_unavailable, {"Retry-After": "5"}),
        (DriverError("57P03"), "GET", ErrorCode.service_unavailable, {"Retry-After": "5"}),
        (wrapped(None, invalidated=True), "GET", ErrorCode.service_unavailable, {"Retry-After": "5"}),
        (ConnectionRefusedError(), "GET", ErrorCode.service_unavailable, {"Retry-After": "5"}),
        (socket.gaierror(), "GET", ErrorCode.service_unavailable, {"Retry-After": "5"}),
        (OSError("Multiple exceptions: [Errno 61] ..."), "GET", ErrorCode.service_unavailable, {"Retry-After": "5"}),
        (PoolTimeoutError(), "GET", ErrorCode.service_unavailable, {"Retry-After": "5"}),
    ],
)
def test_classify(exc: Exception, method: str, code: ErrorCode, headers: dict[str, str]) -> None:
    result = classify(exc, method)

    assert result.code is code
    assert result.headers == headers
    assert "driver message" not in result.detail


@pytest.mark.parametrize(
    "exc",
    [
        wrapped("22P02"),
        wrapped("22000"),
        wrapped("23502", IntegrityError),
        wrapped("23514", IntegrityError),
        wrapped("25P02"),
        wrapped("42P01"),
        wrapped("XX000"),
        wrapped(None),
        DriverError("28P01"),
        RuntimeError("bug"),
        KeyError("bug"),
    ],
)
def test_everything_else_is_an_internal_error(exc: Exception) -> None:
    result = classify(exc, "POST")

    assert result.code is ErrorCode.internal_error
    assert result.detail == "Internal Server Error"
    assert result.headers == {}
