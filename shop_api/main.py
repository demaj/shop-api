import logging
from contextlib import asynccontextmanager
from http import HTTPStatus
from uuid import uuid4

from asgi_correlation_id import CorrelationIdFilter, CorrelationIdMiddleware
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware

from core.bootstrap import ensure_first_superuser
from core.config import Settings, get_settings
from core.database import async_engine
from core.errors import ApiError
from core.exception_handlers import api_error_handler, http_exception_handler, validation_exception_handler
from core.middleware import ProblemMiddleware, add_process_time_header, log_requests
from core.openapi import PROBLEM_RESPONSES, add_problem_schemas
from helpers.constants import CORRELATION_ID
from routers.api import api_router

# Logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# App Settings
settings: Settings = get_settings()


def configure_logging() -> None:
    handler = logging.StreamHandler()
    handler.addFilter(CorrelationIdFilter(default_value="-"))
    handler.setFormatter(logging.Formatter("%(levelname)s: %(name)s: [%(correlation_id)s] %(message)s"))
    logging.basicConfig(level=logging.INFO, handlers=[handler], force=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    logger.info("Application started")
    await ensure_first_superuser()
    yield
    await async_engine.dispose()
    logger.info("Application shutdown")


app = FastAPI(
    title=settings.PROJECT_TITLE,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.PROJECT_VERSION,
    lifespan=lifespan,
    responses=PROBLEM_RESPONSES,
)
add_problem_schemas(app)

app.add_exception_handler(ApiError, api_error_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

app.add_middleware(ProblemMiddleware)
app.add_middleware(BaseHTTPMiddleware, dispatch=add_process_time_header)
app.add_middleware(BaseHTTPMiddleware, dispatch=log_requests)
app.add_middleware(
    CorrelationIdMiddleware,
    header_name="X-Request-Id",
    update_request_header=True,
    generator=lambda: str(uuid4()),
)

# CORS outermost so preflight and error responses also carry the headers.
if settings.cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=[CORRELATION_ID],
    )


@app.get("/", summary="Status", status_code=HTTPStatus.OK)
async def index() -> dict[str, str]:
    return {"status": "OK"}


app.include_router(api_router)
