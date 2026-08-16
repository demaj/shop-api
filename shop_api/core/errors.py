import logging
from http import HTTPStatus

from sqlalchemy.exc import DBAPIError, IntegrityError
from starlette.requests import Request
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)

PG_FOREIGN_KEY_VIOLATION = "23503"
PG_UNIQUE_VIOLATION = "23505"


async def integrity_error_handler(request: Request, exc: IntegrityError) -> JSONResponse:
    # Registered app-level: a violation surfacing at the request-transaction commit
    # (dependency teardown) cannot be caught by handler-local try/except.
    sqlstate = getattr(exc.orig, "sqlstate", None) or getattr(exc.orig, "pgcode", None)
    if sqlstate == PG_UNIQUE_VIOLATION:
        return JSONResponse(
            status_code=HTTPStatus.CONFLICT,
            content={"detail": "A resource with these values already exists"},
        )
    if sqlstate == PG_FOREIGN_KEY_VIOLATION:
        detail = (
            "Resource is still referenced by other resources"
            if request.method == "DELETE"
            else "Referenced resource does not exist"
        )
        return JSONResponse(status_code=HTTPStatus.CONFLICT, content={"detail": detail})
    logger.exception("Unhandled integrity error")
    return JSONResponse(
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        content={"detail": "Internal Server Error"},
    )


async def dbapi_error_handler(request: Request, exc: DBAPIError) -> JSONResponse:
    # SQLSTATE class 22 ("data exception", e.g. NUL byte 22021) is a client error, not a 500.
    sqlstate = getattr(exc.orig, "sqlstate", None) or getattr(exc.orig, "pgcode", None) or ""
    if sqlstate.startswith("22"):
        logger.info("Rejected invalid input value (sqlstate %s)", sqlstate)
        return JSONResponse(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            content={"detail": "Invalid input value"},
        )
    logger.exception("Unhandled database error")
    return JSONResponse(
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        content={"detail": "Internal Server Error"},
    )
