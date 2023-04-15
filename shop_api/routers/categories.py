from http import HTTPStatus
from typing import Any

from fastapi import APIRouter, Depends, Path
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
    "/",
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
        **filters.dict(exclude_none=True),
        **pagination.dict(),
    }

    query = "SELECT categories.id, categories.name FROM categories"

    if filters.name:
        query += " WHERE name = :name"
        params |= {"name": filters.name}

    query += " LIMIT :limit OFFSET :offset"

    results = await db.execute(statement=text(query), params=params)
    return {
        "filters": filters.dict(),
        "paging": pagination.dict(),
        "results": [result for result in results],
    }


@router.post(
    "/",
    response_model=schemas.Category,
    summary="Create a Category",
    status_code=HTTPStatus.CREATED,
)
async def create_category(
    category_in: schemas.CategoryCreate,
    db: AsyncSession = Depends(get_db),
) -> schemas.Category:
    """
    Create a new `Category`.
    """

    params: dict[str, Any] = {
        **category_in.dict(exclude_none=True),
    }

    query = """
        INSERT INTO categories(name)
        VALUES (:name)
        RETURNING id
    """

    category_id = await db.execute(statement=text(query), params=params) or None
    return params | {**category_id.first()}


@router.put(
    "/{category_id}",
    response_model=schemas.Category,
    status_code=HTTPStatus.OK,
)
async def update_category(
    category_in: schemas.CategoryBase,
    category_id: str = Path(title="The ID of the `category` to update"),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """
    Update a `Category`.
    """

    params: dict[str, Any] = {
        "id": category_id,
        **category_in.dict(exclude_none=True),
    }

    query: str = """
        UPDATE categories
        SET name = :name
        WHERE id = :id
    """

    await db.execute(statement=query, params=params)
    return params


@router.get(
    "/{category_id}",
    response_model=schemas.Category,
    status_code=HTTPStatus.OK,
)
async def read_category(
    category_id: str = Path(title="The ID of the `category` to get"),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """
    Get `Category` by ID.
    """

    params: dict[str, str] = {"id": category_id}

    query = """
        SELECT
            categories.id,
            categories.name
        FROM categories
        WHERE id = :id
        LIMIT 1
    """

    results = await db.execute(statement=text(query), params=params) or None
    return results.first()


@router.delete(
    "/{category_id}",
    status_code=HTTPStatus.NO_CONTENT,
)
async def delete_category(
    category_id: str = Path(title="The ID of the `category` to delete"),
    db: AsyncSession = Depends(get_db),
) -> None:
    """
    Delete a `Category`.
    """

    params: dict[str, str] = {"id": category_id}

    query = "DELETE FROM categories WHERE id=:id RETURNING id"

    await db.execute(statement=text(query), params=params)
