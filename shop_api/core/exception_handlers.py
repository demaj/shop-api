from http import HTTPStatus
from typing import Any

from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from starlette.requests import Request

from core.errors import ApiError, ErrorCode
from core.problems import ProblemResponse, problem_response
from schemas.problem import FieldError

CODE_BY_STATUS: dict[int, ErrorCode] = {
    HTTPStatus.BAD_REQUEST: ErrorCode.bad_request,
    HTTPStatus.UNAUTHORIZED: ErrorCode.unauthenticated,
    HTTPStatus.FORBIDDEN: ErrorCode.forbidden,
    HTTPStatus.NOT_FOUND: ErrorCode.route_not_found,
    HTTPStatus.METHOD_NOT_ALLOWED: ErrorCode.method_not_allowed,
}


async def api_error_handler(request: Request, exc: ApiError) -> ProblemResponse:
    return problem_response(request.scope, exc.code, exc.detail, headers=exc.headers)


async def http_exception_handler(request: Request, exc: HTTPException) -> ProblemResponse:
    code = CODE_BY_STATUS.get(exc.status_code)
    if code is None:
        return problem_response(request.scope, ErrorCode.internal_error, "Internal Server Error", exc=exc)
    detail = exc.detail if isinstance(exc.detail, str) else HTTPStatus(exc.status_code).phrase
    return problem_response(request.scope, code, detail, headers=exc.headers)


def _field_error(error: dict[str, Any]) -> FieldError:
    source, *path = error["loc"] or ("body",)
    code, detail = error["type"], error["msg"]
    if source != "body":
        return FieldError(parameter=".".join(str(part) for part in path), code=code, detail=detail)
    if code == "json_invalid":
        return FieldError(code=code, detail=detail)
    pointer = "".join("/" + str(part).replace("~", "~0").replace("/", "~1") for part in path)
    return FieldError(pointer=pointer, code=code, detail=detail)


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> ProblemResponse:
    unique = {error.model_dump_json(): error for error in map(_field_error, exc.errors())}
    return problem_response(
        request.scope,
        ErrorCode.validation_failed,
        "Request validation failed",
        errors=list(unique.values()),
    )
