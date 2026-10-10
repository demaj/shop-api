from typing import Any

from fastapi import FastAPI
from pydantic.json_schema import models_json_schema

from schemas.problem import Problem

REF_TEMPLATE = "#/components/schemas/{model}"
PROBLEM_CONTENT = {"application/problem+json": {"schema": {"$ref": REF_TEMPLATE.format(model="Problem")}}}

PROBLEM_RESPONSES: dict[int | str, dict[str, Any]] = {
    422: {"description": "Validation Error", "content": PROBLEM_CONTENT},
    "default": {"description": "Error", "content": PROBLEM_CONTENT},
}


def add_problem_schemas(app: FastAPI) -> None:
    generate = app.openapi

    def openapi() -> dict[str, Any]:
        if app.openapi_schema is None:
            _, definitions = models_json_schema([(Problem, "serialization")], ref_template=REF_TEMPLATE)
            generate()["components"]["schemas"].update(definitions["$defs"])
        return app.openapi_schema

    app.openapi = openapi
