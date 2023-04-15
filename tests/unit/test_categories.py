import pytest
from httpx import AsyncClient

BASE_URL = "/categories"


# @pytest.mark.anyio
# async def test_read_categories(async_client: AsyncClient):
#     response = await async_client.get(BASE_URL)
#     assert response.status_code == 200
#     assert response.json() == {"status": "OK"}

# @pytest.mark.anyio
# async def test_create_category(async_client: AsyncClient):
#     response = await async_client.post()
#     assert response.status_code == 200
#     assert response.json() == {"status": "OK"}
