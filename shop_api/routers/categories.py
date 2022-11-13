from http import HTTPStatus

from fastapi import APIRouter, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession

import schemas
import crud
from core.dependencies import get_db
from core.database import AsyncSessionLocal
from filters import CategoryFilter
from pagination import CategoryPagination
from responses import CategoryListResponse

from .tags import Tags

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
) -> dict:
    """
    Retrieve List of `Categories`.
    """

    query_values = {**pagination.dict()}

    query = """SELECT * FROM categories;"""

    results = await db.execute(query, params=query_values)
    return {
        "filters": filters.dict(),
        "paging": pagination.dict(),
        "results": [result for result in results],
    }


@router.post(
    "/",
    # response_model=schemas.CategoryCreate,
    summary="Create a Category",
    status_code=HTTPStatus.CREATED,
)
async def create_category(
    category_in: schemas.CategoryCreate,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Create a new `Category`.
    """

    query = f"""INSERT INTO categories(name) VALUES ('{category_in.name}');"""

    # TODO: Fix: It gets into a loop.
    results = await crud.category.create(db=db, obj_in=category_in)
    print("RESULTS: ", results)
    return results


@router.put(
    "/{category_id}",
    response_model=schemas.Category,
    status_code=HTTPStatus.OK,
)
async def update_category(
    *,
    category_id: int = Path(title="The ID of the `category` to update"),
    category_in: schemas.CategoryBase,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Update a `Category`.
    """

    query = """UPDATE FROM categories WHERE ('Tea');"""

    results = await db.execute(query)
    return results


@router.get(
    "/{category_id}",
    response_model=schemas.Category,
    status_code=HTTPStatus.OK,
)
async def read_category(
    category_id: int = Path(title="The ID of the `category` to get"),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Get `Category` by ID.
    """
    query = """SELECT * FROM categories WHERE :id=;"""

    results = await db.execute(query)
    return results


@router.delete(
    "/{category_id}",
    response_model=schemas.Category,
    status_code=HTTPStatus.OK,
)
async def delete_category(
    category_id: str = Path(title="The ID of the `category` to delete"),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Delete a `Category`.
    """

    query = """DELETE FROM categories WHERE :id=;"""

    results = await db.execute(query)

    return results
