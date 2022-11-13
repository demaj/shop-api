from http import HTTPStatus

from fastapi import APIRouter, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession

import schemas
from core.dependencies import get_db
from filters import ProductFilter
from pagination import ProductPagination
from responses import ProductListResponse

from .tags import Tags

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
) -> dict:
    """
    Retrieve List of `Products`.
    """

    query_values = {**pagination.dict()}

    query = "SELECT * FROM products;"

    results = await db.execute(query, params=query_values)
    return {
        "filters": filters.dict(),
        "paging": pagination.dict(),
        results: [result for result in results],
    }


@router.post(
    "/",
    response_model=schemas.ProductCreate,
    summary="Create a product",
    status_code=HTTPStatus.CREATED,
)
async def create_product(
    product_in: schemas.ProductCreate,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Create a new `Product`.
    """

    query = f"""INSERT INTO product VALUES('{product_in.name}') * FROM products;"""
    results = await db.execute(query)
    return results


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

    query = "SELECT * FROM products;"
    results = await db.execute(query)
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

    query = "SELECT * FROM products;"
    results = await db.execute(query)
    return results
