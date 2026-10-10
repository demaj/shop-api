import logging
import time
from collections.abc import Callable

from asgi_correlation_id import correlation_id
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from core.errors import classify
from core.problems import log_unsent_problem, problem_response, withheld

logger = logging.getLogger(__name__)


async def add_process_time_header(request: Request, call_next: Callable) -> Response:
    start_time = time.time()
    response: Response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


async def log_requests(request: Request, call_next: Callable) -> Response:
    logger.info("Incoming request: %s", correlation_id.get())
    response: Response = await call_next(request)
    logger.info("Outgoing response: %s", correlation_id.get())
    return response


class ProblemMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        started = False

        async def send_tracking_start(message: Message) -> None:
            nonlocal started
            if message["type"] == "http.response.start":
                started = True
            await send(message)

        try:
            await self.app(scope, receive, send_tracking_start)
        except Exception as exc:
            if started:
                log_unsent_problem(scope, exc)
                safe = withheld(exc)
                if safe is exc:
                    raise
                raise safe from None
            code, detail, headers = classify(exc, scope["method"])
            response = problem_response(scope, code, detail, headers=headers, exc=exc)
            await response(scope, receive, send)
