import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_main_app(async_client: AsyncClient):
    response = await async_client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "OK"}
