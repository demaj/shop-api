import logging
import time
from contextlib import asynccontextmanager
from http import HTTPStatus
from typing import Callable, Dict
from uuid import uuid4

from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI
from fastapi.security import HTTPBasic
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import Response

from core.config import Settings, get_settings
from helpers.constants import CORRELATION_ID
from routers import categories, products

# Logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# App Settings
settings: Settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application started")
    yield
    logger.info("Application shutdown")


app = FastAPI(
    title=settings.PROJECT_TITLE,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.PROJECT_VERSION,
    openapi_prefix=settings.API_V1_STR,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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

security = HTTPBasic()


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
async def index() -> Dict[str, str]:
    return {"status": "OK"}


app.include_router(categories.router)
app.include_router(products.router)
