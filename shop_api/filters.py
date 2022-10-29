from fastapi import Query
from pydantic import BaseModel


class BaseFilter(BaseModel):
    class Config:
        use_enum_values = True


class CategoryFilter(BaseFilter):
    name: str | None = Query(
        default=None,
        title="Category name",
        description="The name of the `category` to get",
        min_length=3,
        max_length=50,
    )


class ProductFilter(BaseFilter):
    name: str | None = Query(
        default=None,
        title="Product name",
        description="The name of the `product` to get",
        min_length=3,
        max_length=50,
    )
    price: float | None = Query(
        default=None,
        title="Product price",
        description="The price of the `product` you want to get",
    )
    available: bool | None = Query(
        default=None,
        title="Product Availability",
        description="Is the `product` currently available",
    )
