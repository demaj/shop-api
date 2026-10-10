import logging
from collections.abc import Iterator, Mapping
from http import HTTPStatus

from asgi_correlation_id import correlation_id
from fastapi.exceptions import ValidationException
from starlette.responses import JSONResponse
from starlette.types import Scope

from core.errors import STATUS, ErrorCode, get_constraint, get_sqlstate, is_database_error
from schemas.problem import FieldError, Problem

logger = logging.getLogger(__name__)


class ProblemResponse(JSONResponse):
    media_type = "application/problem+json"


def _related(exc: BaseException) -> Iterator[BaseException]:
    seen: set[int] = set()
    pending = [exc]
    while pending:
        current = pending.pop()
        if current is None or id(current) in seen:
            continue
        seen.add(id(current))
        yield current
        pending += [current.__cause__, current.__context__, *getattr(current, "exceptions", ())]


def withheld(exc: Exception) -> Exception:
    if not any(is_database_error(e) or isinstance(e, ValidationException) for e in _related(exc)):
        return exc
    substitute = RuntimeError(f"{type(exc).__name__}: message withheld")
    return substitute.with_traceback(exc.__traceback__)


def _route(scope: Scope) -> str:
    return getattr(scope.get("route"), "path", "-")


def _level(code: ErrorCode, exc: Exception | None) -> int:
    if STATUS[code] >= HTTPStatus.INTERNAL_SERVER_ERROR:
        return logging.ERROR
    if code is ErrorCode.validation_failed and exc is not None:
        return logging.WARNING
    return logging.INFO


def log_unsent_problem(scope: Scope, exc: Exception) -> None:
    logger.error(
        "problem after response started method=%s route=%s exc=%s",
        scope.get("method", "-"),
        _route(scope),
        type(exc).__name__,
        exc_info=withheld(exc),
    )


def problem_response(
    scope: Scope,
    code: ErrorCode,
    detail: str,
    *,
    headers: Mapping[str, str] | None = None,
    errors: list[FieldError] | None = None,
    exc: Exception | None = None,
) -> ProblemResponse:
    status = STATUS[code]
    logger.log(
        _level(code, exc),
        "problem status=%d code=%s method=%s route=%s exc=%s sqlstate=%s constraint=%s",
        status,
        code,
        scope.get("method", "-"),
        _route(scope),
        type(exc).__name__ if exc else "-",
        get_sqlstate(exc) or "-",
        get_constraint(exc) or "-",
        exc_info=withheld(exc) if exc is not None and code is ErrorCode.internal_error else None,
    )
    problem = Problem(
        title=status.phrase,
        status=status,
        detail=detail,
        code=code,
        request_id=correlation_id.get(),
        errors=errors,
    )
    return ProblemResponse(
        problem.model_dump(mode="json", exclude_none=True),
        status_code=status,
        headers=dict(headers) if headers else None,
    )
