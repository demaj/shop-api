from datetime import datetime
from enum import Enum
from typing import Union
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, HttpUrl, Required, validator


class ProductStatus(str, Enum):
    available = "available"
    pending = "pending"
    sold = "sold"


class ProductImage(BaseModel):
    url: HttpUrl
    name: str


class ProductBase(BaseModel):
    name: Union[str, None] = None
    description: Union[str, None] = Field(default=None, title="The description of the `product`", max_length=300)
    price: Union[float, None] = None
    status: ProductStatus = Field(default=ProductStatus.available, title="Product status")
    category_id: UUID = Field(default=None, title="Category ID")
    tags: Union[set[str], None] = set()
    created: Union[datetime, None] = None
    updated: Union[datetime, None] = None


class ProductCreate(ProductBase):
    name: str = Field(default=Required, title="The name of the `product`", max_length=50)
    price: float = Field(default=Required, gt=0, description="The price of the `product`")

    @validator("price")
    def price_check(cls, v):
        return round(v, 2)


class Product(ProductCreate):
    id: UUID = Field(title="Product ID", default_factory=uuid4)
    description: str

    class Config:
        orm_mode = True
