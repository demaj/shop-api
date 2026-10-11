"""Guards against the dual-import-root trap: overrides must key on the objects routes use."""

from collections.abc import Iterator

from fastapi import FastAPI
from fastapi.dependencies.models import Dependant
from fastapi.routing import APIRoute, iter_route_contexts

from core.dependencies import get_db


def iter_dependencies(dependant: Dependant) -> Iterator[Dependant]:
    for dependency in dependant.dependencies:
        yield dependency
        yield from iter_dependencies(dependency)


def session_dependencies(app: FastAPI) -> list[Dependant]:
    return [
        dependency
        for context in iter_route_contexts(app.routes)
        if isinstance(context.original_route, APIRoute)
        for dependency in iter_dependencies(context.original_route.dependant)
        if dependency.call is get_db
    ]


def test_get_db_is_the_object_routes_were_built_with(app: FastAPI) -> None:
    assert session_dependencies(app), (
        "core.dependencies.get_db is not in the app's dependency graph — module identity split"
    )


def test_every_session_is_closed_before_the_response_is_sent(app: FastAPI) -> None:
    assert {dependency.scope for dependency in session_dependencies(app)} == {"function"}
