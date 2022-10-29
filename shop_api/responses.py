from pydantic import BaseModel

from schemas import Category, Product


class ListResponse(BaseModel):
    filters: dict | None
    pagination: dict | None


class CategoryListResponse(ListResponse):
    results: list[Category]


class ProductListResponse(ListResponse):
    results: list[Product]
