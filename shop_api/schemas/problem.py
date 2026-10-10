from pydantic import BaseModel

from core.errors import ErrorCode


class FieldError(BaseModel):
    pointer: str | None = None
    parameter: str | None = None
    code: str
    detail: str


class Problem(BaseModel):
    type: str = "about:blank"
    title: str
    status: int
    detail: str
    code: ErrorCode
    request_id: str | None = None
    errors: list[FieldError] | None = None
