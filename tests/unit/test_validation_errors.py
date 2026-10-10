import logging
from collections.abc import Iterator

import pytest
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from httpx import AsyncClient
from starlette.requests import Request

import models
from core.dependencies import get_current_user
from core.exception_handlers import validation_exception_handler

pytestmark = pytest.mark.anyio

AUTH = {"Authorization": "Bearer any"}
SECRET = "sh0rt!"


@pytest.fixture
def superuser(app: FastAPI) -> Iterator[None]:
    user = models.User(email="admin@example.com", hashed_password="x", is_active=True, is_superuser=True)
    app.dependency_overrides[get_current_user] = lambda: user
    yield
    app.dependency_overrides.clear()


async def test_body_errors_use_json_pointers_and_do_not_echo_input(superuser: None, async_client: AsyncClient) -> None:
    response = await async_client.post("/api/v1/users", json={"email": "nope", "password": SECRET}, headers=AUTH)

    assert response.status_code == 422
    assert response.headers["content-type"] == "application/problem+json"
    body = response.json()
    assert body["code"] == "validation_failed"
    assert body["detail"] == "Request validation failed"
    assert body["request_id"] == response.headers["x-request-id"]
    assert [(e["pointer"], e["code"]) for e in body["errors"]] == [
        ("/email", "value_error"),
        ("/password", "string_too_short"),
    ]
    assert SECRET not in response.text
    assert "input" not in response.text


async def test_query_and_path_errors_name_the_parameter(async_client: AsyncClient, caplog) -> None:
    with caplog.at_level(logging.INFO, logger="core.problems"):
        query = await async_client.get("/api/v1/products?limit=1000&bogus=1")
    assert [record.levelno for record in caplog.records] == [logging.INFO]
    path = await async_client.get("/api/v1/products/not-a-uuid")

    assert [(e["parameter"], e["code"]) for e in query.json()["errors"]] == [
        ("limit", "less_than_equal"),
        ("bogus", "extra_forbidden"),
    ]
    assert [(e["parameter"], e["code"]) for e in path.json()["errors"]] == [("product_id", "uuid_parsing")]


async def test_malformed_json_has_neither_pointer_nor_parameter(superuser: None, async_client: AsyncClient) -> None:
    response = await async_client.post(
        "/api/v1/categories", content=b'{"name": ', headers={**AUTH, "Content-Type": "application/json"}
    )

    assert response.status_code == 422
    assert response.json()["errors"] == [{"code": "json_invalid", "detail": "JSON decode error"}]


async def test_nested_pointer_is_escaped_and_duplicates_are_removed() -> None:
    error = {"type": "missing", "loc": ("body", "items", 0, "a/b~c"), "msg": "Field required", "input": {"x": 1}}
    request = Request({"type": "http", "method": "POST", "headers": []})

    response = await validation_exception_handler(request, RequestValidationError([error, dict(error)]))

    assert response.status_code == 422
    assert b'"errors":[{"pointer":"/items/0/a~1b~0c","code":"missing","detail":"Field required"}]' in response.body
