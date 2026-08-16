import logging
import time
from collections.abc import Callable
from contextlib import asynccontextmanager
from http import HTTPStatus
from uuid import uuid4

from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI
from sqlalchemy.exc import DBAPIError, IntegrityError
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import Response

from core.bootstrap import ensure_first_superuser
from core.config import Settings, get_settings
from core.database import async_engine
from core.errors import dbapi_error_handler, integrity_error_handler
from helpers.constants import CORRELATION_ID
from routers.api import api_router

# Logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# App Settings
settings: Settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
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
)

app.add_exception_handler(IntegrityError, integrity_error_handler)
app.add_exception_handler(DBAPIError, dbapi_error_handler)

if settings.cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=[CORRELATION_ID],
    )

app.add_middleware(
    CorrelationIdMiddleware,
    header_name="X-Request-Id",
    update_request_header=True,
    generator=lambda: str(uuid4()),
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next: Callable) -> Response:
    start_time = time.time()
    response: Response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.middleware("http")
async def log_requests(request: Request, call_next: Callable) -> Response:
    _correlation_id = request.headers.get(CORRELATION_ID)
    logger.info(f"Incoming request: {_correlation_id}")
    response: Response = await call_next(request)
    _correlation_id = response.headers.get(CORRELATION_ID)
    logger.info(f"Outgoing response: {_correlation_id}")
    return response


@app.get("/", summary="Status", status_code=HTTPStatus.OK)
async def index() -> dict[str, str]:
    return {"status": "OK"}


app.include_router(api_router)
