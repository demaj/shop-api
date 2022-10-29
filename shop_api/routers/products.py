from http import HTTPStatus

from fastapi import APIRouter, Depends

import schemas
from filters import ProductFilter
from pagination import ProductPagination
from responses import ProductListResponse

from .tags import Tags

router = APIRouter(prefix="/products", tags=[Tags.products])


@router.get(
    "/",
    response_model=ProductListResponse,
    status_code=HTTPStatus.OK,
)
async def read_products(filters: ProductFilter = Depends(), pagination: ProductPagination = Depends()) -> dict:
    """
    Retrieve products.
    """
    return {}


@router.post(
    "/",
    response_model=schemas.Product,
    status_code=HTTPStatus.CREATED,
)
async def create_product(product_in: schemas.ProductCreate) -> dict:
    """
    Create new product.
    """
    return {}


@router.put(
    "/{id}",
    response_model=schemas.Product,
    status_code=HTTPStatus.OK,
)
async def update_product(id: int, product_in: schemas.ProductBase) -> dict:
    """
    Update a product.
    """
    return {}


@router.get(
    "/{id}",
    response_model=schemas.Product,
    status_code=HTTPStatus.OK,
)
async def read_product(id: int) -> dict:
    """
    Get product by ID.
    """
    return {}


@router.delete(
    "/{id}",
    response_model=schemas.Product,
    status_code=HTTPStatus.OK,
)
async def delete_product(id: int) -> dict:
    """
    Delete a product.
    """
    return {}
