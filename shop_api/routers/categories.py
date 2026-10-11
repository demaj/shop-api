from http import HTTPStatus
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, Path, Query

import crud
import models
import schemas
from core.dependencies import SessionDep, get_current_active_user
from core.errors import ApiError, ErrorCode
from helpers.params import CategoryListParams
from helpers.responses import CategoryListResponse
from helpers.tags import Tags

# Same prefix, two routers: write_router carries the auth dependency (Phase 3),
# so the decorator you type determines protection.
read_router = APIRouter(prefix="/categories", tags=[Tags.categories])
write_router = APIRouter(
    prefix="/categories",
    tags=[Tags.categories],
    dependencies=[Depends(get_current_active_user)],
)


@read_router.get(
    "",
    response_model=CategoryListResponse,
    status_code=HTTPStatus.OK,
)
async def read_categories(
    db: SessionDep,
    params: Annotated[CategoryListParams, Query()],
) -> dict[str, Any]:
    """
    Retrieve List of `Categories`.
    """

    results = await crud.category.get_page(db, params=params)
    return {
        "filters": params.filters(),
        "paging": params.paging(),
        "results": results,
    }


@write_router.post(
    "",
    response_model=schemas.CategoryRead,
    summary="Create a Category",
    status_code=HTTPStatus.CREATED,
)
async def create_category(
    db: SessionDep,
    category_in: schemas.CategoryCreate,
) -> models.Category:
    """
    Create a new `Category`.
    """

    return await crud.category.create(db, obj_in=category_in)


@write_router.put(
    "/{category_id}",
    response_model=schemas.CategoryRead,
    status_code=HTTPStatus.OK,
)
async def update_category(
    db: SessionDep,
    category_in: schemas.CategoryUpdate,
    category_id: UUID = Path(title="The ID of the `category` to update"),
) -> models.Category:
    """
    Update a `Category`.
    """

    changes = category_in.changes()
    if not changes:
        raise ApiError(ErrorCode.validation_failed, "No updatable fields provided")

    category = await crud.category.get(db, category_id)
    if category is None:
        raise ApiError(ErrorCode.resource_not_found, f"Category {category_id} not found")
    return await crud.category.update(db, db_obj=category, changes=changes)


@read_router.get(
    "/{category_id}",
    response_model=schemas.CategoryRead,
    status_code=HTTPStatus.OK,
)
async def read_category(
    db: SessionDep,
    category_id: UUID = Path(title="The ID of the `category` to get"),
) -> models.Category:
    """
    Get `Category` by ID.
    """

    category = await crud.category.get(db, category_id)
    if category is None:
        raise ApiError(ErrorCode.resource_not_found, f"Category {category_id} not found")
    return category


@write_router.delete(
    "/{category_id}",
    status_code=HTTPStatus.NO_CONTENT,
)
async def delete_category(
    db: SessionDep,
    category_id: UUID = Path(title="The ID of the `category` to delete"),
) -> None:
    """
    Delete a `Category`.
    """

    category = await crud.category.get(db, category_id)
    if category is None:
        raise ApiError(ErrorCode.resource_not_found, f"Category {category_id} not found")
    await crud.category.remove(db, db_obj=category)
