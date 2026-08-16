from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from schemas.product import ProductStatus


class BaseListParams(BaseModel):
    """Merged filter + pagination query params (FastAPI supports one query model per endpoint)."""

    model_config = ConfigDict(extra="forbid")

    offset: int = Field(default=0, ge=0, le=2_147_483_647)
    limit: int = Field(default=100, ge=1, le=100)

    def filters(self) -> dict[str, Any]:
        return self.model_dump(mode="json", exclude={"offset", "limit"})

    def paging(self) -> dict[str, Any]:
        return self.model_dump(mode="json", include={"offset", "limit"})


class CategoryListParams(BaseListParams):
    limit: int = Field(default=10, ge=1, le=100)
    name: str | None = Field(
        default=None,
        min_length=3,
        max_length=50,
        description="The name of the `Category` to get",
    )


class ProductListParams(BaseListParams):
    name: str | None = Field(
        default=None,
        min_length=3,
        max_length=50,
        description="The name of the `Product` to get",
    )
    price: int | None = Field(
        default=None,
        ge=0,
        le=2_147_483_647,
        description="The price of the `Product` you want to get, in cents",
    )
    status: ProductStatus | None = Field(
        default=None,
        description="Only return `Products` with this status",
    )
