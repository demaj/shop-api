from http import HTTPStatus
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, Path, Query

import crud
import models
import schemas
from core.dependencies import SessionDep, get_current_active_user
from core.errors import ApiError, ErrorCode
from helpers.params import ProductListParams
from helpers.responses import ProductListResponse
from helpers.tags import Tags

# Same prefix, two routers: write_router carries the auth dependency (Phase 3),
# so the decorator you type determines protection.
read_router = APIRouter(prefix="/products", tags=[Tags.products])
write_router = APIRouter(
    prefix="/products",
    tags=[Tags.products],
    dependencies=[Depends(get_current_active_user)],
)


@read_router.get(
    "",
    response_model=ProductListResponse,
    status_code=HTTPStatus.OK,
)
async def read_products(
    db: SessionDep,
    params: Annotated[ProductListParams, Query()],
) -> dict[str, Any]:
    """
    Retrieve List of `Products`.
    """

    results = await crud.product.get_page(db, params=params)
    return {
        "filters": params.filters(),
        "paging": params.paging(),
        "results": results,
    }


@write_router.post(
    "",
    response_model=schemas.ProductRead,
    summary="Create a Product",
    status_code=HTTPStatus.CREATED,
)
async def create_product(
    db: SessionDep,
    product_in: schemas.ProductCreate,
) -> models.Product:
    """
    Create a new `Product`.
    """

    return await crud.product.create(db, obj_in=product_in)


@write_router.put(
    "/{product_id}",
    response_model=schemas.ProductRead,
    status_code=HTTPStatus.OK,
)
async def update_product(
    db: SessionDep,
    *,
    product_id: UUID = Path(title="The ID of the `Product` to update"),
    product_in: schemas.ProductUpdate,
) -> models.Product:
    """
    Update a `Product`.
    """

    changes = product_in.changes()
    if not changes:
        raise ApiError(ErrorCode.validation_failed, "No updatable fields provided")

    product = await crud.product.get(db, product_id)
    if product is None:
        raise ApiError(ErrorCode.resource_not_found, f"Product {product_id} not found")
    return await crud.product.update(db, db_obj=product, changes=changes)


@read_router.get(
    "/{product_id}",
    response_model=schemas.ProductRead,
    status_code=HTTPStatus.OK,
)
async def read_product(
    db: SessionDep,
    product_id: UUID = Path(title="The ID of the `Product` to get"),
) -> models.Product:
    """
    Get `Product` by ID.
    """

    product = await crud.product.get(db, product_id)
    if product is None:
        raise ApiError(ErrorCode.resource_not_found, f"Product {product_id} not found")
    return product


@write_router.delete(
    "/{product_id}",
    status_code=HTTPStatus.NO_CONTENT,
)
async def delete_product(
    db: SessionDep,
    product_id: UUID = Path(title="The ID of the `Product` to delete"),
) -> None:
    """
    Delete a `Product`.
    """

    product = await crud.product.get(db, product_id)
    if product is None:
        raise ApiError(ErrorCode.resource_not_found, f"Product {product_id} not found")
    await crud.product.remove(db, db_obj=product)
