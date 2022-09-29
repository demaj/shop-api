from typing import Dict

import schemas
from fastapi import APIRouter, Depends
from filters import ProductFilter

from ..pagination import CategoryPagination
from ..responses import ProductListResponse

router = APIRouter(prefix="/products")


@router.get("/", response_model=ProductListResponse)
async def read_products(filters: ProductFilter = Depends(), pagination: CategoryPagination = Depends()) -> Dict:
    """Retrieve products."""
    return {}


@router.post("/", response_model=schemas.Product)
async def create_product(product_in: schemas.ProductCreate) -> Dict:
    """Create new product."""
    return {}


@router.put("/{id}", response_model=schemas.Product)
async def update_product(id: int, product_in: schemas.ProductBase) -> Dict:
    """Update a product."""
    return {}


@router.get("/{id}", response_model=schemas.Product)
async def read_product(id: int) -> Dict:
    """Get product by ID."""
    return {}


@router.delete("/{id}", response_model=schemas.Product)
async def delete_product(id: int) -> Dict:
    """Delete a product."""
    return {}
