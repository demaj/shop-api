import json
import logging

import pytest
from httpx import AsyncClient
from starlette.exceptions import HTTPException
from starlette.requests import Request

from core.exception_handlers import http_exception_handler

pytestmark = pytest.mark.anyio

PROBLEM = "application/problem+json"


def request() -> Request:
    return Request({"type": "http", "method": "GET", "headers": []})


async def test_unknown_route_is_a_404_problem(async_client: AsyncClient) -> None:
    response = await async_client.get("/api/v1/nope")

    assert response.status_code == 404
    assert response.headers["content-type"] == PROBLEM
    assert response.json() == {
        "type": "about:blank",
        "title": "Not Found",
        "status": 404,
        "detail": "Not Found",
        "code": "route_not_found",
        "request_id": response.headers["x-request-id"],
    }


async def test_wrong_method_is_a_405_problem_with_allow(async_client: AsyncClient) -> None:
    response = await async_client.post("/")

    assert response.status_code == 405
    assert response.headers["content-type"] == PROBLEM
    assert response.headers["allow"] == "GET"
    assert response.json()["code"] == "method_not_allowed"


async def test_missing_token_is_a_401_problem_with_challenge(async_client: AsyncClient) -> None:
    response = await async_client.get("/api/v1/users/me")

    assert response.status_code == 401
    assert response.headers["content-type"] == PROBLEM
    assert response.headers["www-authenticate"] == "Bearer"
    assert response.json()["code"] == "unauthenticated"


async def test_detail_of_the_exception_is_kept() -> None:
    response = await http_exception_handler(request(), HTTPException(404, "Product 3f2a not found"))

    assert json.loads(response.body)["detail"] == "Product 3f2a not found"


async def test_detail_that_is_not_a_string_is_replaced_by_the_status_phrase() -> None:
    response = await http_exception_handler(request(), HTTPException(400, {"sql": "SELECT secret"}))

    assert json.loads(response.body)["detail"] == "Bad Request"
    assert b"secret" not in response.body


@pytest.mark.parametrize("status", [409, 418, 422, 429, 503])
async def test_status_outside_the_catalogue_is_a_logged_500(status: int, caplog) -> None:
    with caplog.at_level(logging.INFO, logger="core.problems"):
        response = await http_exception_handler(request(), HTTPException(status, "teapot"))

    assert response.status_code == 500
    assert json.loads(response.body)["code"] == "internal_error"
    assert json.loads(response.body)["detail"] == "Internal Server Error"
    (record,) = caplog.records
    assert record.levelno == logging.ERROR
