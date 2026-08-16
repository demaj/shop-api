from http import HTTPStatus
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

import schemas
from core.dependencies import get_db
from helpers.filters import CategoryFilter
from helpers.pagination import CategoryPagination
from helpers.responses import CategoryListResponse
from helpers.tags import Tags

router = APIRouter(prefix="/categories", tags=[Tags.categories])


@router.get(
    "",
    response_model=CategoryListResponse,
    response_model_exclude_none=True,
    status_code=HTTPStatus.OK,
)
async def read_categories(
    db: AsyncSession = Depends(get_db),
    filters: CategoryFilter = Depends(),
    pagination: CategoryPagination = Depends(),
) -> dict[str, Any]:
    """
    Retrieve List of `Categories`.
    """

    params: dict[str, Any] = {
        **filters.model_dump(exclude_none=True),
        **pagination.model_dump(),
    }

    query = "SELECT categories.id, categories.name FROM categories"

    if filters.name:
        query += " WHERE name = :name"
        params |= {"name": filters.name}

    query += " LIMIT :limit OFFSET :offset"

    results = await db.execute(statement=text(query), params=params)
    return {
        "filters": filters.model_dump(),
        "paging": pagination.model_dump(),
        "results": list(results.mappings()),
    }


@router.post(
    "",
    response_model=schemas.Category,
    summary="Create a Category",
    status_code=HTTPStatus.CREATED,
)
async def create_category(
    category_in: schemas.CategoryCreate,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """
    Create a new `Category`.
    """

    params: dict[str, Any] = {
        **category_in.model_dump(exclude_none=True),
    }

    query = """
        INSERT INTO categories(name)
        VALUES (:name)
        RETURNING id, name
    """

    result = await db.execute(statement=text(query), params=params)
    return dict(result.mappings().first())


@router.put(
    "/{category_id}",
    response_model=schemas.Category,
    status_code=HTTPStatus.OK,
)
async def update_category(
    category_in: schemas.CategoryUpdate,
    category_id: UUID = Path(title="The ID of the `category` to update"),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """
    Update a `Category`.
    """

    if category_in.name is None:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail="No updatable fields provided",
        )

    params: dict[str, Any] = {
        "id": category_id,
        "name": category_in.name,
    }

    query = """
        UPDATE categories
        SET name = :name
        WHERE id = :id
        RETURNING id, name
    """

    result = await db.execute(statement=text(query), params=params)
    row = result.mappings().first()
    if row is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"Category {category_id} not found")
    return dict(row)


@router.get(
    "/{category_id}",
    response_model=schemas.Category,
    status_code=HTTPStatus.OK,
)
async def read_category(
    category_id: UUID = Path(title="The ID of the `category` to get"),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """
    Get `Category` by ID.
    """

    params: dict[str, Any] = {"id": category_id}

    query = """
        SELECT
            categories.id,
            categories.name
        FROM categories
        WHERE id = :id
        LIMIT 1
    """

    result = await db.execute(statement=text(query), params=params)
    row = result.mappings().first()
    if row is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"Category {category_id} not found")
    return dict(row)


@router.delete(
    "/{category_id}",
    status_code=HTTPStatus.NO_CONTENT,
)
async def delete_category(
    category_id: UUID = Path(title="The ID of the `category` to delete"),
    db: AsyncSession = Depends(get_db),
) -> None:
    """
    Delete a `Category`.
    """

    params: dict[str, Any] = {"id": category_id}

    query = "DELETE FROM categories WHERE id = :id RETURNING id"

    result = await db.execute(statement=text(query), params=params)
    if result.first() is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"Category {category_id} not found")
