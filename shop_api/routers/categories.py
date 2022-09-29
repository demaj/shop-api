from typing import Dict

import schemas
from fastapi import APIRouter, Depends
from filters import CategoryFilter

from ..pagination import CategoryPagination
from ..responses import CategoryListResponse

router = APIRouter(prefix="/categories")


@router.get("/", response_model=CategoryListResponse, response_model_exclude_none=True)
async def read_categories(filters: CategoryFilter = Depends(), pagination: CategoryPagination = Depends()) -> Dict:
    """
    Retrieve Categories.
    """
    return {}


@router.post("/", response_model=schemas.Category)
async def create_category(category_in: schemas.CategoryCreate) -> Dict:
    """
    Create new Category.
    """
    return {}


@router.put("/{id}", response_model=schemas.Category)
async def update_category(id: int, category_in: schemas.CategoryBase) -> Dict:
    """
    Update a Category.
    """
    return {}


@router.get("/{id}", response_model=schemas.Category)
async def read_category(id: int) -> Dict:
    """
    Get category by ID.
    """
    return {}


@router.delete("/{id}", response_model=schemas.Category)
async def delete_category(id: int) -> Dict:
    """
    Delete a category.
    """
    return {}
