from http import HTTPStatus
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path
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
    "",
    response_model=ProductListResponse,
    response_model_exclude_none=True,
    status_code=HTTPStatus.OK,
)
async def read_products(
    db: AsyncSession = Depends(get_db),
    filters: ProductFilter = Depends(),
    pagination: ProductPagination = Depends(),
) -> dict[str, Any]:
    """
    Retrieve List of `Products`.
    """

    params: dict[str, Any] = {**pagination.model_dump()}

    query = "SELECT * FROM products"

    clauses: list[str] = []
    if filters.name:
        clauses.append("name = :name")
        params |= {"name": filters.name}
    if filters.price is not None:
        clauses.append("price = :price")
        params |= {"price": filters.price}
    if filters.status:
        clauses.append("status = :status")
        params |= {"status": filters.status}

    if clauses:
        query += " WHERE " + " AND ".join(clauses)

    query += " LIMIT :limit OFFSET :offset"

    results = await db.execute(statement=text(query), params=params)
    return {
        "filters": filters.model_dump(),
        "paging": pagination.model_dump(),
        "results": list(results.mappings()),
    }


@router.post(
    "",
    response_model=schemas.Product,
    summary="Create a Product",
    status_code=HTTPStatus.CREATED,
)
async def create_product(
    product_in: schemas.ProductCreate,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """
    Create a new `Product`.
    """

    params: dict[str, Any] = product_in.model_dump(
        exclude_none=True,
        include={"name", "description", "price", "status", "category_id"},
    )
    params["status"] = product_in.status.value

    columns = ", ".join(params)
    binds = ", ".join(f":{column}" for column in params)
    query = f"""
        INSERT INTO products({columns})
        VALUES ({binds})
        RETURNING id, name, description, price, status, category_id, created, updated
    """

    result = await db.execute(statement=text(query), params=params)
    return dict(result.mappings().first())


@router.put(
    "/{product_id}",
    response_model=schemas.Product,
    status_code=HTTPStatus.OK,
)
async def update_product(
    *,
    product_id: UUID = Path(title="The ID of the `Product` to update"),
    product_in: schemas.ProductUpdate,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """
    Update a `Product`.
    """

    data: dict[str, Any] = product_in.model_dump(
        exclude_unset=True,
        include={"name", "description", "price", "status", "category_id"},
    )
    # description is the only nullable column; an explicit null elsewhere means "unchanged"
    data = {key: value for key, value in data.items() if value is not None or key == "description"}
    if not data:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail="No updatable fields provided",
        )
    if "status" in data:
        data["status"] = product_in.status.value

    assignments = ", ".join(f"{column} = :{column}" for column in data)
    query = f"""
        UPDATE products
        SET {assignments}, updated = now()
        WHERE id = :id
        RETURNING id, name, description, price, status, category_id, created, updated
    """

    result = await db.execute(statement=text(query), params={**data, "id": product_id})
    row = result.mappings().first()
    if row is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"Product {product_id} not found")
    return dict(row)


@router.get(
    "/{product_id}",
    response_model=schemas.Product,
    status_code=HTTPStatus.OK,
)
async def read_product(
    product_id: UUID = Path(title="The ID of the `Product` to get"),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """
    Get `Product` by ID.
    """

    query = "SELECT * FROM products WHERE id = :id LIMIT 1"

    result = await db.execute(statement=text(query), params={"id": product_id})
    row = result.mappings().first()
    if row is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"Product {product_id} not found")
    return dict(row)


@router.delete(
    "/{product_id}",
    status_code=HTTPStatus.NO_CONTENT,
)
async def delete_product(
    product_id: UUID = Path(title="The ID of the `Product` to delete"),
    db: AsyncSession = Depends(get_db),
) -> None:
    """
    Delete a `Product`.
    """

    query = "DELETE FROM products WHERE id = :id RETURNING id"

    result = await db.execute(statement=text(query), params={"id": product_id})
    if result.first() is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"Product {product_id} not found")
