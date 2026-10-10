import json

from fastapi import FastAPI

from core.errors import ErrorCode

PROBLEM = {"application/problem+json": {"schema": {"$ref": "#/components/schemas/Problem"}}}


def operations(schema: dict) -> list[dict]:
    return [operation for path in schema["paths"].values() for operation in path.values()]


def test_every_operation_documents_problem_responses(app: FastAPI) -> None:
    for operation in operations(app.openapi()):
        assert operation["responses"]["default"]["content"] == PROBLEM
        assert operation["responses"]["422"]["content"] == PROBLEM


def test_problem_schemas_replace_the_default_validation_error(app: FastAPI) -> None:
    schemas = app.openapi()["components"]["schemas"]

    assert {"Problem", "FieldError", "ErrorCode"} <= set(schemas)
    assert "HTTPValidationError" not in schemas
    assert schemas["ErrorCode"]["enum"] == [code.value for code in ErrorCode]


def test_every_schema_reference_resolves(app: FastAPI) -> None:
    schema = app.openapi()
    references = {part.split('"')[0] for part in json.dumps(schema).split('"$ref": "#/components/schemas/')[1:]}

    assert references <= set(schema["components"]["schemas"])
