from typing import Dict, List, Optional

from pydantic import BaseModel

from .schemas import Category, Product


class ListResponse(BaseModel):
    filters: Optional[Dict]
    pagination: Optional[Dict]


class CategoryListResponse(ListResponse):
    results: List[Category]


class ProductListResponse(ListResponse):
    results: List[Product]
