from http import HTTPStatus

import pytest
from httpx import AsyncClient

from helpers.params import ProductListParams

pytestmark = pytest.mark.anyio


@pytest.mark.parametrize(
    "query",
    [
        "limit=-1",
        "limit=0",
        "limit=101",
        "offset=-1",
        "offset=9223372036854775808",
        "unknown_param=1",
        "price=-5",
        "status=bogus",
    ],
)
async def test_invalid_params_are_422(async_client: AsyncClient, query: str) -> None:
    # Query validation fails before the handler (and its DB dependency) runs.
    response = await async_client.get(f"/api/v1/products?{query}")
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_filters_and_paging_split() -> None:
    params = ProductListParams(offset=5, limit=20, name="Tea", status="sold")
    assert params.paging() == {"offset": 5, "limit": 20}
    assert params.filters() == {"name": "Tea", "price": None, "status": "sold"}
