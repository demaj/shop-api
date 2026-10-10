from collections.abc import Mapping
from enum import StrEnum
from http import HTTPStatus
from typing import NamedTuple

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.exc import TimeoutError as PoolTimeoutError


class ErrorCode(StrEnum):
    bad_request = "bad_request"
    unauthenticated = "unauthenticated"
    invalid_credentials = "invalid_credentials"
    forbidden = "forbidden"
    account_inactive = "account_inactive"
    route_not_found = "route_not_found"
    resource_not_found = "resource_not_found"
    method_not_allowed = "method_not_allowed"
    already_exists = "already_exists"
    reference_not_found = "reference_not_found"
    resource_in_use = "resource_in_use"
    validation_failed = "validation_failed"
    internal_error = "internal_error"
    service_unavailable = "service_unavailable"


STATUS: dict[ErrorCode, HTTPStatus] = {
    ErrorCode.bad_request: HTTPStatus.BAD_REQUEST,
    ErrorCode.unauthenticated: HTTPStatus.UNAUTHORIZED,
    ErrorCode.invalid_credentials: HTTPStatus.UNAUTHORIZED,
    ErrorCode.forbidden: HTTPStatus.FORBIDDEN,
    ErrorCode.account_inactive: HTTPStatus.FORBIDDEN,
    ErrorCode.route_not_found: HTTPStatus.NOT_FOUND,
    ErrorCode.resource_not_found: HTTPStatus.NOT_FOUND,
    ErrorCode.method_not_allowed: HTTPStatus.METHOD_NOT_ALLOWED,
    ErrorCode.already_exists: HTTPStatus.CONFLICT,
    ErrorCode.reference_not_found: HTTPStatus.CONFLICT,
    ErrorCode.resource_in_use: HTTPStatus.CONFLICT,
    ErrorCode.validation_failed: HTTPStatus.UNPROCESSABLE_ENTITY,
    ErrorCode.internal_error: HTTPStatus.INTERNAL_SERVER_ERROR,
    ErrorCode.service_unavailable: HTTPStatus.SERVICE_UNAVAILABLE,
}


class ApiError(Exception):
    def __init__(self, code: ErrorCode, detail: str, headers: Mapping[str, str] | None = None) -> None:
        super().__init__(detail)
        self.code = code
        self.detail = detail
        self.headers = headers


def get_sqlstate(exc: Exception | None) -> str | None:
    return getattr(getattr(exc, "orig", exc), "sqlstate", None)


def get_constraint(exc: Exception | None) -> str | None:
    return getattr(getattr(getattr(exc, "orig", None), "__cause__", None), "constraint_name", None)


def is_database_error(exc: BaseException) -> bool:
    return isinstance(exc, SQLAlchemyError) or getattr(exc, "sqlstate", None) is not None


class Classified(NamedTuple):
    code: ErrorCode
    detail: str
    headers: Mapping[str, str]


UNIQUE_VIOLATION = "23505"
FOREIGN_KEY_VIOLATION = "23503"
INVALID_INPUT = {"22001", "22003", "22021"}
TRANSACTION_CONFLICT = {"40001", "40P01"}
QUERY_CANCELED = "57014"
SERVER_UNAVAILABLE = {"57P01", "57P02", "57P03"}
CONNECTION_CLASSES = {"08", "53"}

RETRY_NOW = {"Retry-After": "1"}
RETRY_LATER = {"Retry-After": "5"}


def classify(exc: Exception, method: str) -> Classified:
    sqlstate = get_sqlstate(exc) or ""
    if sqlstate == UNIQUE_VIOLATION:
        return Classified(ErrorCode.already_exists, "A resource with these values already exists", {})
    if sqlstate == FOREIGN_KEY_VIOLATION:
        if method == "DELETE":
            return Classified(ErrorCode.resource_in_use, "Resource is still referenced by other resources", {})
        return Classified(ErrorCode.reference_not_found, "Referenced resource does not exist", {})
    if sqlstate in INVALID_INPUT:
        return Classified(ErrorCode.validation_failed, "Invalid input value", {})
    if sqlstate in TRANSACTION_CONFLICT:
        return Classified(ErrorCode.service_unavailable, "Service temporarily unavailable", RETRY_NOW)
    if sqlstate == QUERY_CANCELED or isinstance(exc, TimeoutError):
        return Classified(ErrorCode.service_unavailable, "Service temporarily unavailable", {})
    if (
        sqlstate[:2] in CONNECTION_CLASSES
        or sqlstate in SERVER_UNAVAILABLE
        or getattr(exc, "connection_invalidated", False)
        or isinstance(exc, (OSError, PoolTimeoutError))
    ):
        return Classified(ErrorCode.service_unavailable, "Service temporarily unavailable", RETRY_LATER)
    return Classified(ErrorCode.internal_error, "Internal Server Error", {})
