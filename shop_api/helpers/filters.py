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
    price: int | None = Query(
        default=None,
        ge=0,
        le=2_147_483_647,
        title="Product's price",
        description="The price of the `Product` you want to get, in cents",
    )
    status: ProductStatus | None = Query(
        default=None,
        title="Product's status",
        description="Only return `Products` with this status",
    )
