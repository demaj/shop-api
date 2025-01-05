from fastapi import Query
from pydantic import BaseModel, ConfigDict

from schemas.product import ProductStatus


class BaseFilter(BaseModel):
    model_config = ConfigDict(use_enum_values=True)


class CategoryFilter(BaseFilter):
    name: str | None = Query(
        default=None,
        title="Category's name",
        description="The name of the `Category` to get",
        min_length=3,
        max_length=50,
    )


class ProductFilter(BaseFilter):
    name: str | None = Query(
        default=None,
        title="Product's name",
        description="The name of the `Product` to get",
        min_length=3,
        max_length=50,
    )
    price: float | None = Query(
        default=None,
        title="Product's price",
        description="The price of the `Product` you want to get",
    )
    available: ProductStatus | None = Query(
        default=ProductStatus.available,
        title="Product's availability",
        description="Is the `Product` currently available",
    )
