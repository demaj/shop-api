"""Guards against the dual-import-root trap: overrides must key on the objects routes use."""

from collections.abc import Iterator
from typing import Any

from fastapi import FastAPI
from fastapi.dependencies.models import Dependant
from fastapi.routing import APIRoute

from core.dependencies import get_db


def iter_dependency_calls(dependant: Dependant) -> Iterator[Any]:
    for dependency in dependant.dependencies:
        yield dependency.call
        yield from iter_dependency_calls(dependency)


def test_get_db_is_the_object_routes_were_built_with(app: FastAPI) -> None:
    calls = {
        call for route in app.routes if isinstance(route, APIRoute) for call in iter_dependency_calls(route.dependant)
    }
    assert get_db in calls, "core.dependencies.get_db is not in the app's dependency graph — module identity split"
