from http import HTTPStatus
from typing import Any

from fastapi import APIRouter, Depends, Path
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

import schemas
from core.dependencies import get_db
from helpers.filters import ProductFilter
from helpers.pagination import ProductPagination
from helpers.responses import ProductListResponse
from helpers.tags import Tags

router = APIRouter(prefix="/products", tags=[Tags.products])


@router.get(
    "/",
    response_model=ProductListResponse,
    response_model_exclude_none=True,
    status_code=HTTPStatus.OK,
)
async def read_products(
    db: AsyncSession = Depends(get_db),
    filters: ProductFilter = Depends(),
    pagination: ProductPagination = Depends(),
) -> ProductListResponse:
    """
    Retrieve List of `Products`.
    """

    params: dict[str, Any] = {
        **filters.model_dump(exclude_none=True),
        **pagination.model_dump(),
    }

    query = "SELECT * FROM products"

    if filters.name:
        query += " name = :name"
        params |= {"name": filters.name}

    query += " LIMIT :limit OFFSET :offset"

    results = await db.execute(statement=text(query), params=params)
    return {
        "filters": filters.model_dump(),
        "paging": pagination.model_dump(),
        "results": [result for result in results],
    }


@router.post(
    "/",
    response_model=schemas.ProductCreate,
    summary="Create a Product",
    status_code=HTTPStatus.CREATED,
)
async def create_product(
    product_in: schemas.ProductCreate,
    db: AsyncSession = Depends(get_db),
) -> schemas.Category:
    """
    Create a new `Product`.
    """

    params: dict[str, Any] = {
        **product_in.model_dump(exclude_none=True),
    }

    query = """
        INSERT INTO product(name, price)
        VALUES (:name, :price)
    """

    product_id = await db.execute(statement=text(query), params=params) or None
    return params | dict(product_id.mappings().first())


@router.put(
    "/{product_id}",
    response_model=schemas.Product,
    status_code=HTTPStatus.OK,
)
async def update_product(
    *,
    product_id: str = Path(title="The ID of the `Product` to update"),
    product_in: schemas.ProductBase,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Update a `Product`.
    """

    query = "SELECT * FROM products;"
    results = await db.execute(query)
    return results


@router.get(
    "/{id}",
    response_model=schemas.Product,
    status_code=HTTPStatus.OK,
)
async def read_product(
    product_id: str = Path(title="The ID of the `Product` to get"),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Get `Product` by ID.
    """

    query = "SELECT * FROM products WHERE id=;"

    results = await db.fetch_one(query)
    return results


@router.delete(
    "/{id}",
    response_model=schemas.Product,
    status_code=HTTPStatus.OK,
)
async def delete_product(
    product_id: str = Path(title="The ID of the `Product` to delete"),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Delete a `Product`.
    """
    params = {**product_id.model_dump(exclude_none=True)}

    query = "DELETE FROM products WHERE id = :id"
    results = await db.execute(statement=text(query), params=params)
    return results
