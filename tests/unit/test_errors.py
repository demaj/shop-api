from core.errors import STATUS, ErrorCode


def test_every_code_has_exactly_one_status() -> None:
    assert set(STATUS) == set(ErrorCode)


def test_code_to_status_table_is_pinned() -> None:
    assert {code.value: int(status) for code, status in STATUS.items()} == {
        "bad_request": 400,
        "unauthenticated": 401,
        "invalid_credentials": 401,
        "forbidden": 403,
        "account_inactive": 403,
        "route_not_found": 404,
        "resource_not_found": 404,
        "method_not_allowed": 405,
        "already_exists": 409,
        "reference_not_found": 409,
        "resource_in_use": 409,
        "payload_too_large": 413,
        "validation_failed": 422,
        "rate_limited": 429,
        "internal_error": 500,
        "service_unavailable": 503,
    }
