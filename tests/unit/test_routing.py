"""Structural invariants: no unprotected writes, everything under /api/v1."""

from fastapi import FastAPI
from fastapi.dependencies.utils import get_flat_dependant
from fastapi.routing import APIRoute

WRITE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}
# Explicit, reviewable allowlist of intentionally public write endpoints.
PUBLIC_WRITE_PATHS = {"/api/v1/auth/token"}


def api_routes(app: FastAPI) -> list[APIRoute]:
    return [route for route in app.routes if isinstance(route, APIRoute)]


def test_every_write_route_requires_authentication(app: FastAPI) -> None:
    unprotected = []
    for route in api_routes(app):
        if not (route.methods & WRITE_METHODS) or route.path in PUBLIC_WRITE_PATHS:
            continue
        if not get_flat_dependant(route.dependant).security_requirements:
            unprotected.append(f"{sorted(route.methods)} {route.path}")
    assert not unprotected, f"Write routes without authentication: {unprotected}"


def test_all_api_routes_are_versioned(app: FastAPI) -> None:
    unversioned = [
        route.path for route in api_routes(app) if route.path != "/" and not route.path.startswith("/api/v1/")
    ]
    assert not unversioned, f"Routes outside /api/v1: {unversioned}"


def test_openapi_token_url(app: FastAPI) -> None:
    schema = app.openapi()
    flows = schema["components"]["securitySchemes"]["OAuth2PasswordBearer"]["flows"]
    assert flows["password"]["tokenUrl"] == "/api/v1/auth/token"
