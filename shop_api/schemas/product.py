from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator


class ProductStatus(str, Enum):
    available = "available"
    pending = "pending"
    sold = "sold"


class ProductImage(BaseModel):
    url: HttpUrl
    name: str


class ProductBase(BaseModel):
    name: str | None = None
    description: str | None = Field(default=None, title="The description of the `product`", max_length=300)
    price: float | None = None
    status: ProductStatus = Field(default=ProductStatus.available, title="Product status")
    category_id: UUID = Field(default=None, title="Category ID")
    tags: set[str] | None = set()
    created: datetime | None = None
    updated: datetime | None = None


class ProductCreate(ProductBase):
    name: str = Field(title="The name of the `product`", max_length=50)
    price: float = Field(gt=0, description="The price of the `product`")

    @field_validator("price")
    @classmethod
    def price_check(cls, v):
        return round(v, 2)


class Product(ProductCreate):
    id: UUID = Field(title="Product ID", default_factory=uuid4)
    description: str
    model_config = ConfigDict(from_attributes=True)
