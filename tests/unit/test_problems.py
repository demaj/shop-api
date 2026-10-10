import json
import logging
from types import SimpleNamespace

import pytest
from asgi_correlation_id import correlation_id
from fastapi.exceptions import ResponseValidationError
from sqlalchemy.exc import IntegrityError, PendingRollbackError

from core.errors import ErrorCode
from core.problems import problem_response
from schemas import FieldError

SCOPE = {"type": "http", "method": "GET", "route": SimpleNamespace(path="/api/v1/products/{product_id}")}


def body(response) -> dict:
    return json.loads(response.body)


def test_problem_body_and_media_type() -> None:
    token = correlation_id.set("9b1c")
    try:
        response = problem_response(SCOPE, ErrorCode.resource_not_found, "Product not found")
    finally:
        correlation_id.reset(token)

    assert response.status_code == 404
    assert response.media_type == "application/problem+json"
    assert body(response) == {
        "type": "about:blank",
        "title": "Not Found",
        "status": 404,
        "detail": "Product not found",
        "code": "resource_not_found",
        "request_id": "9b1c",
    }


def test_headers_and_field_errors_are_included() -> None:
    response = problem_response(
        SCOPE,
        ErrorCode.validation_failed,
        "Request validation failed",
        headers={"Retry-After": "5"},
        errors=[FieldError(pointer="/password", code="string_too_short", detail="Too short")],
    )

    assert response.headers["retry-after"] == "5"
    assert body(response)["errors"] == [{"pointer": "/password", "code": "string_too_short", "detail": "Too short"}]


@pytest.mark.parametrize(
    ("code", "level"),
    [(ErrorCode.resource_not_found, logging.INFO), (ErrorCode.service_unavailable, logging.ERROR)],
)
def test_one_log_line_with_level_by_status(code: ErrorCode, level: int, caplog) -> None:
    with caplog.at_level(logging.INFO, logger="core.problems"):
        problem_response(SCOPE, code, "x")

    (record,) = caplog.records
    assert record.levelno == level
    assert f"code={code.value} method=GET route=/api/v1/products/{{product_id}}" in record.getMessage()


def test_unmatched_route_is_logged_as_dash(caplog) -> None:
    scope = {"type": "http", "method": "GET", "path": "/x\nERROR: forged"}
    with caplog.at_level(logging.INFO, logger="core.problems"):
        problem_response(scope, ErrorCode.route_not_found, "x")

    assert "route=- " in caplog.records[0].getMessage()
    assert "forged" not in caplog.text


def test_internal_error_logs_traceback(caplog) -> None:
    with caplog.at_level(logging.INFO, logger="core.problems"):
        problem_response(SCOPE, ErrorCode.internal_error, "Internal Server Error", exc=RuntimeError("boom"))

    (record,) = caplog.records
    assert record.exc_info is not None
    assert "exc=RuntimeError" in record.getMessage()


def test_database_error_is_logged_without_its_message(caplog) -> None:
    class FakeDriverError(Exception):
        sqlstate = "23502"

    exc = FakeDriverError("DETAIL: Failing row contains (1, bob@example.com, $argon2id$secret)")
    with caplog.at_level(logging.INFO, logger="core.problems"):
        problem_response(SCOPE, ErrorCode.internal_error, "Internal Server Error", exc=exc)

    (record,) = caplog.records
    assert "sqlstate=23502" in record.getMessage()
    assert "FakeDriverError: message withheld" in caplog.text
    assert "bob@example.com" not in caplog.text


def test_value_rejected_by_the_database_is_logged_as_warning(caplog) -> None:
    class FakeDriverError(Exception):
        sqlstate = "22001"

    with caplog.at_level(logging.INFO, logger="core.problems"):
        problem_response(SCOPE, ErrorCode.validation_failed, "Invalid input value", exc=FakeDriverError())

    (record,) = caplog.records
    assert record.levelno == logging.WARNING
    assert record.exc_info is None


SECRET = "bob@example.com"


class DriverError(Exception):
    sqlstate = "23502"
    constraint_name = None


def integrity_error() -> IntegrityError:
    return IntegrityError("INSERT", {}, DriverError(f"DETAIL: Failing row contains (1, {SECRET}, $argon2id$x)"))


def raised(exc: Exception, *, cause: Exception | None = None, context: Exception | None = None) -> Exception:
    try:
        if context is not None:
            try:
                raise context
            except Exception:
                raise exc  # noqa: B904
        raise exc from cause
    except Exception as caught:
        return caught


@pytest.mark.parametrize(
    "exc",
    [
        integrity_error(),
        raised(RuntimeError("could not save"), cause=integrity_error()),
        raised(KeyError("fallback"), context=integrity_error()),
        PendingRollbackError(f"Original exception was: {integrity_error()}"),
        ExceptionGroup("unhandled errors in a TaskGroup", [integrity_error()]),
        ResponseValidationError(
            [{"type": "value_error", "loc": ("response", "email"), "msg": "bad", "input": SECRET}]
        ),
    ],
    ids=["wrapped", "cause", "context", "pending-rollback", "group", "response-validation"],
)
def test_message_is_withheld_for_any_exception_carrying_data(exc: Exception, caplog) -> None:
    with caplog.at_level(logging.INFO, logger="core.problems"):
        problem_response(SCOPE, ErrorCode.internal_error, "Internal Server Error", exc=exc)

    assert "message withheld" in caplog.text
    assert SECRET not in caplog.text


def test_constraint_name_is_logged(caplog) -> None:
    driver_error = DriverError("x")
    driver_error.__cause__ = type("AsyncpgError", (Exception,), {"constraint_name": "users_email_key"})()
    exc = IntegrityError("INSERT", {}, driver_error)

    with caplog.at_level(logging.INFO, logger="core.problems"):
        problem_response(SCOPE, ErrorCode.already_exists, "x", exc=exc)

    assert "sqlstate=23502 constraint=users_email_key" in caplog.records[0].getMessage()
